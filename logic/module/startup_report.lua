-- Crash reports stay on this device. No telemetry or upload endpoint.
local M = {stage='Starting', report='', recovery=false}
local version='0.2.2'
local report_path
local state_path

local function safe_load(path)
    local ok,value=pcall(sys.load,path)
    return ok and value or {}
end
local function save_report(value)
    M.report=value
    pcall(sys.save,report_path,{text=value})
end
local function number(value)
    if type(value)=='number' then return value end
    return tonumber(tostring(value))
end
local function native_report(handle)
    local lines={'Freaky Fruit Fusion crash report',
        'Reader version: '..version,
        'Engine: '..tostring(crash.get_sys_field(handle,crash.SYSFIELD_ENGINE_VERSION)),
        'Engine hash: '..tostring(crash.get_sys_field(handle,crash.SYSFIELD_ENGINE_HASH)),
        'Device: '..tostring(crash.get_sys_field(handle,crash.SYSFIELD_DEVICE_MODEL)),
        'OS: '..tostring(crash.get_sys_field(handle,crash.SYSFIELD_SYSTEM_VERSION)),
        'Signal: '..tostring(crash.get_signum(handle)),
        'Build: '..tostring(crash.get_user_field(handle,0)),
        'Last stage: '..tostring(crash.get_user_field(handle,1))}
    local modules=crash.get_modules(handle) or {}
    for i,pc in ipairs(crash.get_backtrace(handle) or {}) do
        local address=number(pc)
        local closest,base=nil,-1
        if address then
            for _,module in pairs(modules) do
                local candidate=number(module.address)
                if candidate and candidate<=address and candidate>base then
                    closest,base=module,candidate
                end
            end
        end
        if closest then
            local name=tostring(closest.name):match('[^/]+$') or tostring(closest.name)
            lines[#lines+1]=string.format('#%02d %s +0x%x',i-1,name,address-base)
        else
            lines[#lines+1]=string.format('#%02d %s',i-1,tostring(pc))
        end
    end
    local extra=crash.get_extra_data(handle)
    if extra and #extra>0 then lines[#lines+1]='Details:\n'..extra end
    return table.concat(lines,'\n')
end

function M.set_stage(value)
    M.stage=value
    if crash then pcall(crash.set_user_field,1,value) end
    pcall(sys.save,state_path,{stage=value,version=version})
    print('FRUIT_BOOT: '..value)
end

function M.init()
    report_path=sys.get_save_file('freaky_fruit_fusion','startup_report')
    state_path=sys.get_save_file('freaky_fruit_fusion','startup_state')
    M.report=safe_load(report_path).text or ''
    local previous=safe_load(state_path)
    local handle
    if crash then
        local ok,value=pcall(crash.load_previous)
        if ok then handle=value end
    end
    if handle then
        local ok,value=pcall(native_report,handle)
        if ok then save_report(value) else save_report('Crash report could not be decoded: '..tostring(value)) end
        pcall(crash.release,handle)
        M.recovery=true
    elseif previous.stage and previous.stage~='Game ready' then
        M.recovery=true
        if M.report=='' then
            save_report('The last launch did not finish.\nBuild: '..tostring(previous.version)..
                '\nLast stage: '..tostring(previous.stage)..'\nNo native crash dump was available.')
        end
    end
    if crash then pcall(crash.set_user_field,0,'Freaky Fruit Fusion '..version) end
    sys.set_error_handler(function(source,message,traceback)
        save_report('Lua error in '..tostring(source)..'\nStage: '..M.stage..'\n'..
            tostring(message)..'\n'..tostring(traceback))
        M.recovery=true
        pcall(msg.post,'bootstrap:/go#loading','startup_failed')
    end)
    M.set_stage('Preparing game')
    return M.recovery
end

function M.pages()
    local text=M.report~='' and M.report or ('No saved crash report.\nCurrent stage: '..M.stage)
    text=text:gsub('[^\n\r\t\32-\126]','?')
    local lines={}
    for line in (text..'\n'):gmatch('(.-)\n') do
        if #line==0 then lines[#lines+1]='' end
        while #line>0 do lines[#lines+1]=line:sub(1,48);line=line:sub(49) end
    end
    local pages={}
    for first=1,#lines,23 do
        local page={}
        for i=first,math.min(first+22,#lines) do page[#page+1]=lines[i] end
        pages[#pages+1]=table.concat(page,'\n')
    end
    return pages
end
return M
