local function nginx_scheduler(props)

    nodes = {}
    for _, peer in pairs(props.peers) do
        nodes[peer.hostname] = {}
    end
    return {
        role={
            template='nginx/v1',
            frontend={kind='example'},
        },
        nodes=nodes,
    }

end

return nginx_scheduler
