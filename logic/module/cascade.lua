-- Dropped-fruit identity prevents the direct merge earning a chain bonus.
local M={WINDOW=3.0,MAX_MULTIPLIER=5}
function M.new() return {clock=0,serial=0,items={},chains={},recent=nil} end
function M.update(s,dt)
    s.clock=s.clock+dt
    for key,c in pairs(s.chains) do if s.clock-c.last>15 then s.chains[key]=nil end end
end
function M.drop(s,id)
    s.serial=s.serial+1
    local c={id=s.serial,count=0,last=s.clock}
    s.chains[c.id]=c;s.items[id]={chain=c.id,direct=true};s.recent=c.id
end
function M.start_shake(s)
    s.serial=s.serial+1
    local c={id=s.serial,count=0,last=s.clock}
    s.chains[c.id]=c;s.recent=c.id
end
function M.remove(s,id) s.items[id]=nil end
function M.merge(s,a,b,new_id,tier)
    local aa,bb=s.items[a],s.items[b]
    local direct=(aa and aa.direct) or (bb and bb.direct) or false
    local chain
    for _,item in ipairs({aa or false,bb or false}) do
        local c=item and s.chains[item.chain]
        if c and s.clock-c.last<=M.WINDOW and (not chain or c.count>chain.count) then chain=c end
    end
    if not chain then
        local recent=s.chains[s.recent]
        if recent and s.clock-recent.last<=M.WINDOW then chain=recent end
    end
    if not chain then
        s.serial=s.serial+1;chain={id=s.serial,count=0,last=s.clock};s.chains[chain.id]=chain
    end
    chain.count=chain.count+1;chain.last=s.clock;s.recent=chain.id
    s.items[a],s.items[b]=nil,nil
    if new_id then s.items[new_id]={chain=chain.id,direct=false} end
    local multiplier=direct and 1 or math.min(M.MAX_MULTIPLIER,math.max(2,chain.count))
    local base=2^(tier-1)
    return {points=base*multiplier,base=base,multiplier=multiplier,chain=chain.count,celebrate=not direct}
end
return M
