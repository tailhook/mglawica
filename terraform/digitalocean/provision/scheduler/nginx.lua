-- This is

NGINX_HOST = 'maggie'

local function nginx_scheduler(props)
    return {
        role={
            template='nginx/v1',
            frontend={kind='example'},
        },
        nodes={
            [NGINX_HOST]={}
        }
    }
end

return nginx_scheduler
