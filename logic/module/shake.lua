-- Defold normalizes both Android and iOS acceleration to g units.
-- Gravity filter plus three alternating peaks reject tilts and single bumps.
local M={THRESHOLD=1.45,WINDOW=0.95,COOLDOWN=10,MAX_TIER=3}
function M.new() return {clock=0,ready_at=0,gx=nil,gy=0,gz=0,peaks=0,last_peak=-10,first_peak=-10,last_input=-10} end
function M.update(s,dt) s.clock=s.clock+dt end
function M.remaining(s) return math.max(0,s.ready_at-s.clock) end
function M.consume(s)
    if M.remaining(s)>0 then return false end
    s.ready_at=s.clock+M.COOLDOWN;s.peaks=0;return true
end
function M.input(s,x,y,z)
    local dt=s.clock-s.last_input
    if dt<=0 then return false end
    s.last_input=s.clock
    if not s.gx or dt>0.5 then s.gx,s.gy,s.gz=x,y,z;s.peaks=0;return false end
    local a=1-math.exp(-dt/0.35)
    s.gx=s.gx+(x-s.gx)*a;s.gy=s.gy+(y-s.gy)*a;s.gz=s.gz+(z-s.gz)*a
    local dx,dy,dz=x-s.gx,y-s.gy,z-s.gz
    local mag=math.sqrt(dx*dx+dy*dy+dz*dz)
    if M.remaining(s)>0 or mag<M.THRESHOLD then return false end
    if s.clock-s.first_peak>M.WINDOW then s.peaks=0 end
    if s.clock-s.last_peak<0.10 then return false end
    if s.peaks>0 and dx*s.px+dy*s.py+dz*s.pz > -0.15*mag*s.pm then return false end
    if s.peaks==0 then s.first_peak=s.clock end
    s.peaks=s.peaks+1;s.last_peak=s.clock;s.px,s.py,s.pz,s.pm=dx,dy,dz,mag
    if s.peaks>=3 then s.peaks=0;return true end
    return false
end
return M
