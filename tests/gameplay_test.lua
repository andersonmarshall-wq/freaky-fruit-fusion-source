package.path='./?.lua;'..package.path
local squish=require('logic.module.squish')
local profiles=require('logic.module.fruit_profiles')
local cascade=require('logic.module.cascade')
local shake=require('logic.module.shake')
local function near(a,b,e) assert(math.abs(a-b)<e,string.format('%f ~= %f',a,b)) end
local function loaded(tier,weight,rate)
    local s=squish.new(profiles[tier].softness)
    for i=1,rate*6 do squish.contact(s,'floor',0,1,0,weight);squish.update(s,1/rate) end
    return s
end
local peach=loaded(6,8,60);local coconut=loaded(7,8,60)
assert(peach.rest>.09 and peach.body_scale<.96,'Heavy pile must remain compressed and physically settle')
assert(peach.rest>coconut.rest*4,'Coconut must be substantially firmer than peach')
local lightly=loaded(6,1,60);assert(peach.rest>lightly.rest*2,'More weight must compress more')
local q=peach.rest
for i=1,120 do squish.update(peach,1/60,true) end
near(peach.rest,q,.001) -- Sleeping bodies retain their load.
for i=1,360 do squish.update(peach,1/60,false) end
assert(peach.rest<.0005,'Unloaded fruit must recover')
near(loaded(6,6,30).rest,loaded(6,6,120).rest,.001)
local s=squish.new(1);squish.impact(s,.6,.8,1000)
local peak,rebound=0,0
for i=1,240 do
    squish.update(s,1/120);peak=math.max(peak,s.amount);rebound=math.min(rebound,s.amount)
    local a,b=squish.scales(s);near(a*b,1,1e-9)
    assert(s.amount<=.25 and s.amount>=-.075)
end
assert(peak>.16 and rebound<-.02,'A hard drop needs compression and rebound')
local side=squish.new(1)
for i=1,360 do squish.contact(side,'wall',1,0,0,8);squish.update(side,1/60) end
assert(math.abs(side.nx)>.99,'Side pressure must orient the deformation')

local c=cascade.new();cascade.drop(c,'drop')
local one=cascade.merge(c,'drop','a','grown',1)
assert(not one.celebrate and one.multiplier==1 and one.points==1)
local two=cascade.merge(c,'grown','b','grown2',2)
assert(two.celebrate and two.multiplier==2 and two.points==4)
local three=cascade.merge(c,'grown2','c','grown3',3)
assert(three.celebrate and three.multiplier==3 and three.points==12)
cascade.drop(c,'drop2')
local direct=cascade.merge(c,'drop2','grown3','d',4)
assert(not direct.celebrate and direct.multiplier==1,'A new falling fruit is always direct')
local fresh=cascade.new();cascade.drop(fresh,'falling')
local collateral=cascade.merge(fresh,'pile1','pile2','p',2)
assert(collateral.celebrate and collateral.multiplier==2,'Pile-only merges are indirect')
for i=1,12 do assert(cascade.merge(fresh,'p','other','p',3).multiplier<=5) end
cascade.update(fresh,5)
assert(cascade.merge(fresh,'p','last','new',3).multiplier==2,'Expired cascades restart')

local function sample(s,x,y,z,dt) shake.update(s,dt or 1/60);return shake.input(s,x,y,z) end
local sh=shake.new()
for i=1,180 do assert(not sample(sh,0,math.sin(i/180*math.pi/2),math.cos(i/180*math.pi/2)),'Tilt must not trigger') end
assert(not sample(sh,3,0,1,.12),'A single bump must not trigger')
for i=1,90 do assert(not sample(sh,0,0,1)) end
local triggers=0
for _,x in ipairs({3,-3,3}) do if sample(sh,x,0,1,.16) then triggers=triggers+1 end end
assert(triggers==1,'Three alternating vigorous peaks must trigger once')
assert(shake.consume(sh));assert(not shake.consume(sh))
for i=1,30 do assert(not sample(sh,i%2==0 and -3 or 3,0,1,.12)) end
shake.update(sh,11);assert(shake.consume(sh),'Power-up should recharge')
print(string.format('PASS: pressure/material/frame-rate/recovery, impact/rebound, cascade scoring, shake filtering/cooldown; peak %.3f rebound %.3f',peak,rebound))
