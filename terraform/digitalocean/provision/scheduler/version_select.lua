local version = require "version"


local function lame_select(runtime, parents, actions, now)

    local available_versions = {}
    for ver, _ in pairs(runtime) do
        if ver:find("^v%d") then
            available_versions[#available_versions+1] = ver
        end
    end
    table.sort(available_versions, version.compare)

    -- First, if someone pressed the button, just use latest version pressed
    for _, act in pairs(actions) do
        if act.button and act.button.version then
            print("Version switched by user to", act.button.version)
            -- TODO(pc) check if version is in available versions
            -- TODO(pc) shouldn't timestamp be from the button press ?
            return available_versions, act.button.version, now
        end
    end

    local ver = nil
    local timestamp = 0
    for _, p in pairs(parents) do
        if p.version and p.version_timestamp and
            p.version_timestamp > timestamp
        then
            ver = p.version
            timestamp = p.version_timestamp
        end
    end

    local def_version = available_versions[#available_versions]
    local def_version_timestamp = (runtime[def_version].timestamp or 0)*1000

    if ver ~= nil and def_version_timestamp < timestamp then
        print("Chosen parent version", ver, "with timestamp", timestamp)
        -- Return version timestamp rather than now, in case someone pressed
        -- button on the other side of split brain
        return available_versions, ver, timestamp
    end

    print("Default version is", def_version)
    -- Return zero timestamp, for the case someone have already chosen version
    -- on the other side of the split brain
    return available_versions, def_version, def_version_timestamp
end

return {
    lame_select=lame_select,
}
