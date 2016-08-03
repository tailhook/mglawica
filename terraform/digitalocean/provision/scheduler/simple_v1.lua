local version_select = require "version_select"
local merge = require "merge"
local trace = require "trace"
local func = require "func"

local function simple_v1_scheduler(props)
    local states = props.parents
    local runtime = props.runtime
    local actions = props.actions
    local now = props.now

    local all_ver, ver, timestamp = version_select.lame_select(
        runtime, states, actions, now)
    local settings = runtime.settings or {}
    runtime = runtime[ver]

    local running = true
    local run_timestamp = 0
    for _, item in pairs(states) do
        if item.run_timestamp and item.run_timestamp > run_timestamp then
            running = item.running
            run_timestamp = item.run_timestamp
        end
    end

    for _, act in pairs(actions) do
        if act.button and act.button.stop then
            running = false
            run_timestamp = now
        end
        if act.button and act.button.start then
            running = true
            run_timestamp = now
        end
    end

    trace.object("settings", settings)

    -- default host for staging containers
    local node = "maggie"
    if settings.servers ~= nil then
        -- TODO(pc) use random server, but first check in states
        node = settings.servers[1]
    end
    local nginx_hosts = nil
    for _, daemon in pairs(runtime.daemons) do
        if daemon['http-host'] then
            nginx_hosts = {{
                name=daemon['http-host'],
                targets={{
                    host=node,
                    port=daemon['port'],
                }},
                static_container=daemon.static_container,
                static_host=daemon.static_host,
                static_prefixes=daemon.static_prefixes,
            }}
        end
    end

    return {
        state={version=ver, version_timestamp=timestamp,
               running=running, run_timestamp=run_timestamp},
        role={
            template='simple/v1',
            frontend={kind='version', allow_stop=true},
            versions=all_ver,
            commands=runtime.commands or {},
            ports=settings.ports,
            min_user=settings.min_user,
            user_count=settings.user_count,
            nginx_hosts=nginx_hosts,
        },
        nodes={
            [node]=running and {
                daemons=func.map_pairs(
                    function (k, v)
                        return merge.tables(v, {key=k, instances=1})
                    end,
                    runtime.daemons),
            } or {daemons={}}
        }
    }
end

return simple_v1_scheduler
