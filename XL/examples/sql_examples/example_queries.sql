-- Query config events
%%sql
select event,timedt,clientTime,launchid,clientParams as 'Client parameters',
securityId as 'Security policy ID',
securityName as 'Security policy name',
securityParams as 'Security policy parameters',
sceneV4Id as 'V4 scene strategy ID',
sceneV4Name as 'V4 scene strategy name',
sceneV4AB as 'V4 scene strategy AB group',
--sceneV4Params as 'V4 scene strategy parameters',
userGroupId as 'Current user group ID',
userGroupName as 'Current user group name',
userGroupParams as 'User stratification details',
mediaId as 'Our media (application) ID',
UA as 'User agent',
IP as 'User IP',
cityName as 'City name',
regionName as 'Province name',
mediaId,
UA,
IP,
cityName,
regionName,
uniqueId,
userId,
sourceCid,
channelId,
packageName,
brand,
PCCSDKVersion,
traceId,
accountId,
ggBodyLevel1,
ggBodyLevel2,
clientTime,
onceStayTime
--sceneV4Params

    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-04-15'
        and launchid = (select launchId
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-04-15'
        and qaOAIDMD5 = 'ebe8294b43e225e142ca055b0c014a06'
        and event = 'info'
        order by clienttime desc
        limit 1)

        and event = 'config'
        order by clienttime desc
        limit 100
        ;

-- Query info events
%%sql
select timedt,clientTime,launchid,channelId,PCCSDKVersion,platformVersionCode,platformVersionCode2,versionName,versionCode,packageName,brand,brand2,PCCSDKVersion,
manufacturer,model,osType,osVersionCode,osVersionName,
platformVersionName,screenWidth,screenHeight,deviceType,userId,qaOAIDMD5,qaDeviceIdMD5,
qaAdvertisingIdMD5,idsErrInfo,networkType,sourcePackageName,sourceType,sourceExtra,
traceId,accountId,ggBodyLevel1,ggBodyLevel2,mediaSceneId,mediaSlotId,
sourceCid,cidPath,extraParams,pageId,tId,lbId,launchAuto,launchType
    from ods_RealTime_pcc_quickapp_events
    where
        --timed between '2025-01-01' and '2025-04-15'
        timed = '2025-04-15'
        and event = 'info'
        and userid = '2391ffb6744bde42'
        
    


        --and platformVersionCode2 not in ('90704','90703','90702','90700')
        

        order by clientTime  desc       
        limit 100
        ;

-- Query req2 events
%%sql
select timedt,clientTime,pvid,avid,launchid,reqId,
userGroupId as 'Current user group ID',
sceneV4Id as 'V4 scene strategy ID',
ggPlatform as 'Ad source',
ggId,
ggIdType as 'Ad code type'
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-03-'
        and event = 'req2'
        and launchid in (select launchId
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-03-26'
        and userid = 'b51e5e622dcd1e70'
        and event = 'info'
        order by clienttime desc
        limit 30)

        order by clienttime desc
        limit 50
        ;

-- Query send2 events
%%sql
select timedt,clientTime,event,launchid,reqId,pvid,avid,brand,reqId,
userGroupId,
sceneV4Id,
ggId,
ggIdType,
ggParams,
ggSource,
ggSourceType,
ggPlatform,
poolType,
errCode,
errMsg,
ggTrueStyle,
ggPrePrice,
ggProPrice,
bidPrice
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-02-27'
        and event = 'send2'
        and launchid in (select launchId
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-02-27'
        and userid = '7459f51d29de5961'
        and event = 'info'
        order by clienttime desc
        limit 10)
        order by clienttime desc
        limit 30
        ;

-- Query imp events
%%sql
select timedt,clientTime,event,launchid,pvid,avid,brand,reqId,
userGroupId,
sceneV4Id,
reqId,
userGroupId,
sceneV4Id,
ggId,
ggIdType,
ggParams,
ggSource,
ggSourceType,
ggPlatform,
ggTrueStyle,
impPosition,
impV,
impT,
impW,
isAct,
layerId,
layerBackgroundId,
thenPoolCount,
poolType,
layerLocation,
winSource,
winPrice,
targetCtr,
currentCtr,
impDiff,
reportAdClick
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-03-26'
        and event = 'imp'
        and launchid in (select launchId
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-03-26'
        and userid = '0b844ab2db4d00b4'
        and event = 'info'
        order by clienttime desc
        limit 1000)
        order by clienttime desc
        ;

-- Query another send2 events
%%sql
select timedt,clientTime,event,launchid,reqId,
userGroupId,
sceneV4Id,
ggId,
ggIdType,
ggParams,
ggSource,
ggSourceType,
ggPlatform as 'Added field',
poolType,
errCode,
errMsg as 'Added field 2',
ggTrueStyle,
ggPrePrice,
ggProPrice,
bidPrice,
ggStatus as 'Removed',
ggInteractionType,
dpLink,
ggSourcePkgName,
ggAppInfo,
ggImgList,
appPrivacyUrl,
promotionPurpose,
permissionUrl,
hasPrivacy,
contentType
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-03-26'
        and event = 'send2'
        and launchid in (select launchId
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-03-26'
        and userid = 'e58cac56a55aae7f'
        and event = 'info'
        order by clienttime desc
        limit 1000)


        order by clienttime desc
        ;

-- Query clk events
%%sql
select timedt,clientTime,event,launchid,reqId,
userGroupId,
sceneV4Id,
ggId,
ggIdType,
ggParams,
ggSource,
ggSourceType,
ggPlatform,
clkV,
isAct,
layerId,
reportAdClick,
clickInfo,
clkCount,
isD1Act,
ggSourcePkgName,
layerBackgroundId,
isAct
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-03-26'
        and event = 'clk'
        and launchid in (select launchId
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-03-26'
        and userid = 'b51e5e622dcd1e70'
        and event = 'info'
        order by clienttime desc
        limit 1000)

        order by clienttime desc
        ;

-- Query cls events
%%sql
select timedt,clientTime,event,launchid,reqId,
userGroupId,
sceneV4Id,
ggId,
isEnded,
clsType

    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-03-26'
        and event = 'cls'
        and launchid in (select launchId
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-03-26'
        and userid = 'b51e5e622dcd1e70'
        and event = 'info'
        order by clienttime desc
        limit 1000)
        order by clienttime desc
        ;

-- Query err events
%%sql
select timedt,avid,pvid,brand,clientTime,event,launchid,reqId,
userGroupId,
sceneV4Id,
ggId,
errCode,
errMsg

    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-03-26'
        and event = 'err'
        and launchid in (select launchId
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-03-26'
        and userid = 'e58cac56a55aae7f'
        and event = 'info'
        order by clienttime desc
        limit 1000)
        order by clienttime desc
        limit 100
        
        ;

-- Query all events
%%sql
select timedt,clientTime,event,page,reqId,thenPoolCount,ggId,poolType,ggStatus,ggSourceType,
`ggParams`->'$.creativeType',`ggParams`->'$.isApp',
ggSource,impPosition,winSource,ggPrePrice,ggProPrice,bidPrice,winPrice,targetCtr,currentCtr,trigger,clsType,page,
impPosition,impV,impT,clkV,clsType,
ggIdType,ggStatus,ggSource,ggSourcePkgName,
ggPrePrice,ggProPrice,bidPrice,winPrice,targetCtr,currentCtr,errCode,errMsg
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-04-15'
        and launchid = (select launchId
    from ods.ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-04-15'
        and qaOAIDMD5 = 'ebe8294b43e225e142ca055b0c014a06'
        and event = 'info'
        order by clienttime desc
        limit 1)
        --and impPosition = 'bottom_jlq'
        --and poolType = 'incent_addExpPool'
        --and event = 'clk'
        --and ggSourceType = 'downloadApp'
        --and clsType = 'replaced'
        and event in ('clk','imp')
        --and ggStatus = 'DOWNLOAD'
        --and impPosition = 'bottom'
        --and poolType = 'addExpPool'
        --and brand = 'honor'
        --and clkV = '98'
        --and reqid = 'slotReqId-6113a7d9c47d96b1f581d975a22200db'

        order by clienttime desc
        
        limit 200
    
        ;

-- Query users who clicked on phone complaint
%%sql
select timedt,launchid,userid,brand,brand2,model,sourcePackageName,qaOAIDMD5

FROM ods_RealTime_pcc_quickapp_events

WHERE 
timed = '2025-04-14'
and timedt > '2025-04-14 08:50:00' and timedt < '2025-04-14 09:02:00'
and launchid in (select launchid from ods_RealTime_pcc_quickapp_events where timedt > '2025-04-14 08:50:00' and event = 'clickHotline')
and brand = 'huawei'
and event = 'info'



order by clienttime desc 
limit 500

-- Query users who complained from sidebar
%%sql
select timedt,launchid,userid,brand,brand2,model,sourcePackageName,qaOAIDMD5

FROM ods_RealTime_pcc_quickapp_events

WHERE 
timed = '2025-04-14'
and timedt > '2025-04-14 08:50:00' and timedt < '2025-04-14 09:02:00'
and launchid in (select launchid from ods_RealTime_pcc_quickapp_events where timed = '2025-04-14' and timedt > '2025-04-14 08:50:00' and event = 'clickComplain' 
                 and launchid in (select launchid from ods_RealTime_pcc_quickapp_events where timed = '2025-04-14' and timedt > '2025-04-14 08:50:00' and event = 'info2' and regionName = '河北'
                 ) )

and event = 'info'
and brand = 'huawei'
and model = 'HLK-AL00'

order by clienttime desc 
limit 100

-- Query users who clicked on settings
%%sql
select timedt,launchid,userid,PCCSDKVersion,brand,qaOAIDMD5

FROM ods_RealTime_pcc_quickapp_events

WHERE 
timed = '2025-03-20'
and launchid in (select launchId
    from ods_RealTime_pcc_quickapp_events
    where
        timed = '2025-03-20'
        and event = 'goSet'
        order by clienttime desc
                )
-- -- and brand = 'huawei'
and event = 'info'
and timedt > '2025-03-20 09:50:00' and timedt < '2025-03-20 09:58:00'
order by clienttime  
limit 20

-- Query source package names
%%sql
select sourcePackageName,  count(*)as 'num'
    from ods_RealTime_pcc_quickapp_events
    where 
    timed = '2025-03-28'
    and brand = 'vivo'
    and event = 'info'

    group by 1
    order by 2 desc
    limit 50
```