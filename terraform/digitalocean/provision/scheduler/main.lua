local JSON = require "JSON"
local trace = require "trace"
local func = require "func"
local merge = require "merge"
local split = require "split"

local schedulers = {
  simple_v1=require("simple_v1"),
  nginx=require("nginx"),
}

local function fearful_trim(s)
  if s == nil then return nil end
  return (s:gsub("^%s*(.-)%s*$", "%1"))
end

local function _scheduler(state)

    -- hardcoded role
    state.runtime['nginx'] = {kind='nginx'}

    return JSON:encode(merge.schedules(
        func.map_pairs(function (role_name, role_meta)

            print("-------------- ROLE", role_name, "-----------------")
            local scheduler_name = fearful_trim(role_meta.kind)
            if not scheduler_name or schedulers[scheduler_name] == nil then
              print("unknown scheduler type", scheduler_name)
              return nil
            end

            return schedulers[scheduler_name] {
                role=role_name,
                runtime=state.runtime[role_name],
                actions=split.actions(state, role_name),
                parents=split.states(state, role_name),
                metrics=split.metrics(state, role_name),
                peers=state.peers,
                now=state.now,
            }

        end, state.runtime)))
end

return {
    scheduler=trace.wrap_scheduler(_scheduler),
}
