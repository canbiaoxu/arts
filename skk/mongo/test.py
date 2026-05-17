import asyncio


async def 文档代码():

    from pymongo import MongoClient as mongo_client
    from motor.motor_asyncio import AsyncIOMotorClient as motor_client
    from skk.mongo import ODM, mc, mf, mo

    class My_ODM(ODM):

        def mkconn(self):  # 定义同步连接器
            return mongo_client(host='localhost', port=27017)
    
        async def amkconn(self):  # 定义异步连接器
            return motor_client(host='localhost', port=27017)

    odm = My_ODM()          # 账户ODM
    db = odm['泉州市']      # 库ODM
    sheet = db['希望小学']  # 表ODM

    row1 = {'姓名':'小一', '年龄':11, '幸运数字':[1, 2, 3], '成绩':{'语文':81, '数学':82}}
    row2 = {'姓名':'小二', '年龄':12, '幸运数字':[2, 3, 4], '成绩':{'语文':82, '数学':83}}
    row3 = {'姓名':'小三', '年龄':13, '幸运数字':[3, 4, 5], '成绩':{'语文':83, '数学':84}}
    row4 = {'姓名':'小四', '年龄':14, '幸运数字':[4, 5, 6], '成绩':{'语文':84, '数学':85}}
    row5 = {'姓名':'小五', '年龄':15, '幸运数字':[5, 6, 7], '成绩':{'语文':85, '数学':86}}
    row6 = {'姓名':'小六', '年龄':16, '幸运数字':[6, 7, 8], '成绩':{'语文':86, '数学':87}}

    [
        sheet.insert( row1 )        , await sheet.ainsert( row2 )         ,
        sheet.insert( row3, row4 ) , await sheet.ainsert( row5, row6 )  ,
        sheet.delete( )              , await sheet.adelete( )               ,
        sheet.update( {'年龄': 100} ) ,await sheet.aupdate( {'年龄': 200} ) ,
        sheet.find( )                , await sheet.afind( )            ,  
    ]   

    r1 = sheet.insert( row1 )
    r2 = sheet.insert( row3, row4 )

    r1.inserted_id
    r2.inserted_ids

    [
        mc.年龄 > 10                                                     ,
        mc.年龄 >= 10                                                      ,
        mc.年龄 < 10                                                        ,
        mc.年龄 <= 10                                                    ,
        mc.年龄 == 10                                                      ,
        mc.年龄 != 10                                                     ,
        mc.年级 == mf.isin( '初三', '高二' )                              ,
        mc.年龄 == mf.notin( 10, 30, 45 )                                 ,
        mc.爱好 == mf.contain_all( '画画', '足球' )                          ,
        mc.爱好 == mf.contain_any( '画画', '足球' )                         ,
        mc.爱好 == mf.contain_none( '画画', '足球' )                      ,
        mc.姓名 == mf.re( '小' )                                           ,
        sheet[mc.年龄 > 3][mc.年龄 < 100]                                 ,
        sheet[ (mc.年龄 > 3) & (mc.年龄 < 100) ]                                  ,
        sheet[(mc.年龄<30) | (mc.年龄>30) | (mc.年龄==30) | (mc.年龄==None)] ,
        sheet[ (mc.年龄 > 3) - (mc.年龄 > 100) ]   ,                               
        sheet[ ~(mc.年龄 > 100) ]          ,                                       
    ]
    [
        mc.年级 == mf.isin( )      ,   
        mc.年级 == mf.notin( )      ,  
        mc.爱好 == mf.contain_all( )  ,
        mc.爱好 == mf.contain_any( )  ,
        mc.爱好 == mf.contain_none( ) ,
    ]

    sheet[(mc.年龄>13) | (mc.视力>=4.6)][mc.姓名 == mf.re('小')][~(mc.年龄>15)].find( )
    sheet[(mc.年龄>13) | (mc.视力>=4.6)][mc.姓名 == mf.re('小')][~(mc.年龄>15)].update( {'年级':'初三'} )
    sheet[(mc.年龄>13) | (mc.视力>=4.6)][mc.姓名 == mf.re('小')][~(mc.年龄>15)].delete( )

    sheet[mc.成绩.语文 > 80].find()

    sheet[:]           # 所有数据
    sheet[1:-1]        # 所有数据
    sheet[-1:1]        # 所有数据（逆序）
    sheet[1:]          # 所有数据
    sheet[:1000]       # 第1条 ~ 第1000条
    sheet[:-1000]      # 第1条 ~ 倒数第1000条
    sheet[100:200]     # 第100条 ~ 第200条
    sheet[200:100]     # 第200条 ~ 第100条
    sheet[-300:-2]     # 倒数第300条 ~ 倒数第2条
    sheet[50:-2]       # 第50条 ~ 倒数第2条
    sheet[250:]        # 第250条 ~ 最后1条
    sheet[-250:]       # 倒数第250条 ~ 最后1条
    sheet[1]           # 第1条
    sheet[-1]          # 最后1条
    sheet[::3]         # 以3为间距, 间隔操作所有数据
    sheet[100:200:4]   # 以4为间距, 间隔操作第100条 ~ 第200条

    class mc2(mc):
        姓名 = 年龄 = 幸运数字 = None
        class 成绩:
            语文 = 数学 = None

    sheet[mc.姓名 == '小王'][mc2.年龄 > 10].find()
    sheet[mc.姓名 == '小王'][mc2.成绩.语文 > 80].find()

    sheet[mc.年级=='高一'].order(年龄=False, 姓名=True)[2:4].find()

    sheet[mc.年级=='高一'].order(年龄=True)[1:-1].find()

    sheet[mc.年级=='高一'].order(年龄=False)[-1:1].find()
    sheet.order(年龄=True, 姓名=False).order(年龄=False).find()
    sheet.order(年龄=True, 姓名=False).order().find()
    sheet[mc.年级=='高一']['姓名','年龄'].find()
    sheet[mc.年级=='高一']['姓名']['年龄'].find()
    sheet[mc.年级=='高一']['姓名'][None].find()
    [
        odm.len( )                  , await odm.alen( )                  ,
        db.len( )                   , await db.alen( )                   ,
        sheet.len( )                , await sheet.alen( )                ,
        sheet[ mc.age > 8].len( ) , await sheet[mc.age > 8].alen( ) ,
        odm.get_db_names( )         , await odm.aget_db_names( )         ,
        db.get_sheet_names( )       , await db.aget_sheet_names( )       ,
        db.delete_db( )             , await db.adelete_db( )            ,
        sheet.delete_sheet( )       , await sheet.adelete_sheet( )      ,
    ]

    # 同步方式迭代
    for db in odm:
        for sheet in db:
            ...

    # 异步方式迭代
    async for db in odm:
        async for sheet in db:
            ...
    
    sheet.update( {'年龄': mo.inc( 1 )} )

    mo.inc( 1.5 ),mo.inc( -1.5 ),mo.add( 1, 2, 3 ),mo.push( 1, 2, 3 ),mo.pull( 15 ),mo.popfirst,mo.poplast,mo.rename( '新名称' ),mo.unset,mo.delete

    sheet[mc.姓名=='小六'].update({
        '姓名': 'xiaoliu',          # 修改为‘xiaoliu’
        '年龄': mo.inc(6),          # 自增6
        '幸运数字': mo.push(666),   # 添加666
        '视力': mo.rename('眼力'),  # 字段名改为‘眼力’
        '籍贯': mo.delete,          # 删除此字段
        '成绩.语文': 60,            # 改为60分
        '成绩.数学': mo.inc(-6)     # 减6分
    })

asyncio.run(文档代码())



async def 严格测试():

    from pymongo import MongoClient
    from motor.motor_asyncio import AsyncIOMotorClient as motor_client
    from skk.mongo import ODM, mc, mf, mo

    class My_ODM(ODM):
        
        def mkconn(self):
            return MongoClient(host='localhost', port=27017)
        
        async def amkconn(self):
            return motor_client(host='localhost', port=27017)

    odm = My_ODM()         # 账户ODM
    db, db2 = odm['_test_test_test_', '_test_test_test_2']
    await db2.adelete_db()
    sheet, sheet2 = db['学生', '学生2']
    await sheet2.adelete_sheet()

    async def 重置数据():
        await sheet.adelete()
        assert await sheet.alen() == 0
        assert sheet.len() == 0
        row1 = {'姓名': '小一', '序号':1, '幸运数字':[1, 2, 3], '成绩':{'语文':81, '数学':82}}
        row2 = {'姓名': '小二', '序号':2, '幸运数字':[2, 3, 4], '成绩':{'语文':82, '数学':83}}
        row3 = {'姓名': '小三', '序号':3, '幸运数字':[3, 4, 5], '成绩':{'语文':83, '数学':84}}
        row4 = {'姓名': '小四', '序号':4, '幸运数字':[4, 5, 6], '成绩':{'语文':84, '数学':85}}
        row5 = {'姓名': '小五', '序号':5, '幸运数字':[5, 6, 7], '成绩':{'语文':85, '数学':86}}
        row6 = {'姓名': '小六', '序号':6, '幸运数字':[6, 7, 8], '成绩':{'语文':86, '数学':87}}
        row7 = {'姓名': '小七', '序号':7, '幸运数字':[7, 8, 9], '成绩':{'语文':87, '数学':88}}
        row8 = {'姓名': '小八', '序号':8, '幸运数字':[8, 9, 10], '成绩':{'语文':88, '数学':89}}
        row9 = {'姓名': '小九', '序号':9, '幸运数字':[9, 10, 11], '成绩':{'语文':89, '数学':90}}
        r1 = await sheet.ainsert(row1)
        r2 = sheet.insert(row2)
        r3 = await sheet.ainsert(row3, row4, row5)
        r4 = sheet.insert(row6, row7, row8, row9)
        assert await sheet.alen() == 9
        assert sheet.len() == 9
        r1.inserted_id
        r2.inserted_id
        r3.inserted_ids
        r4.inserted_ids

    # 添加1条数据, 批量添加
    await 重置数据()

    # 查询
    assert sheet.len() == 9

    x = await sheet[3].afind()
    assert type(x) is dict
    assert x['序号'] == 3

    r = await sheet[mc['成绩']['语文'] >= 87][:].afind()
    assert len(r) == 3
    assert r[0]['成绩']['语文'] == 87

    r = await sheet[mc.序号>=2][mc.姓名=='小五'][1].afind()
    assert r['序号'] == 5

    # 修改

    await sheet.aupdate({
        '视力': 5.0,
        '爱好': ['足球', '篮球', '画画', '跳绳'],
        '性别': '男'
    })
    r = await sheet[mc.视力==5][:].afind()
    assert len(r) == 9

    sheet[2:5].update({'性别':'女'})
    r = await sheet[mc.性别=='女'][:].afind()
    assert len(r) == 4
    assert r[0]['序号'] == 2


    await sheet[mc.性别=='男'][:].aupdate({
        '爱好': mo.push('编程', '跑步'),
        '视力': mo.inc(-0.5),
        '身高': 172
    })
    r = await sheet[mc.性别=='男'][mc.爱好==mf.contain_all('编程','跑步')][:].afind()
    assert r
    for x in r:
        assert x['视力'] == 4.5
        assert x['身高'] == 172


    # 删除

    await sheet[mc.序号>=6][:].adelete()
    assert await sheet.alen() == len(await sheet[:].afind()) == 5
    await sheet[:].adelete()
    assert await sheet.alen() == len(await sheet[:].afind()) == 0


    # 成员运算
    await 重置数据()

    r = await sheet[mc.幸运数字==mf.contain_all(2,3,4)][:].afind()
    assert len(r) == 1
    assert r[0]['序号'] == 2
    assert len(await sheet[mc.幸运数字==mf.contain_all()][:].afind()) == 9

    r = await sheet[mc.幸运数字==mf.contain_any(2)][:].afind()
    assert len(r) == 2
    assert r[0]['序号'] == 1
    assert not await sheet[mc.幸运数字==mf.contain_any()][:].afind()

    r = await sheet[mc.幸运数字==mf.contain_none(1,2,3)][:].afind()
    assert len(r) == 6
    assert r[0]['序号'] == 4
    assert len(await sheet[mc.幸运数字==mf.contain_none()][:].afind()) == 9

    r = await sheet[mc.序号==mf.isin(4,5,6)][:].afind()
    assert len(r) == 3
    assert r[0]['序号'] == 4
    assert r[-1]['序号'] == 6
    assert len(await sheet[mc.序号==mf.isin()][:].afind()) == 0

    r = await sheet[mc.序号==mf.notin(4,5,6)][:].afind()
    assert len(r) == 6
    assert len(await sheet[mc.序号==mf.notin()][:].afind()) == 9

    assert len(await sheet[mc.姓名==mf.re('小')][:].afind()) == 9

    # 集合运算

    r = await sheet[ mc.序号>=3 ][ mc.序号<=7 ][:].afind()
    assert len(r) == 5
    assert r[0]['序号'] == 3

    r = await sheet[ (mc.序号<=3) | (mc.序号>=7) ][:].afind()
    assert len(r) == 6
    assert r[3]['序号'] == 7

    r = await sheet[ (mc.序号>3) - (mc.序号>=7) ][:].afind()
    assert len(r) == 3
    assert r[-1]['序号'] == 6

    r = await sheet[ ~(mc.序号>3)][:].afind()
    assert len(r) == 3
    assert r[-1]['序号'] == 3

    # 根据子元素过滤
    r = await sheet[mc.成绩.语文 <= 85][:].afind()
    assert len(r) == 5
    assert r[-1]['序号'] == 5

    # 切片
    r = await sheet[:].afind()
    assert len(r) == 9

    r = await sheet[::2].afind()
    assert len(r) == 5
    assert r[0]['序号'] == 1

    r = await sheet[9:1:2].afind()
    assert len(r) == 5
    assert r[0]['序号'] == 9

    assert len(await sheet[2:8].afind()) == len(sheet[8:2].find()) == len(sheet[2:-2].find()) == len(await sheet[-2:2].afind()) == len(await sheet[-8:8].afind()) == len(await sheet[8:-8].afind()) == 7
    assert len(await sheet[-2:-8].afind()) == len(sheet[-8:-2].find()) == 7

    assert len(await sheet[1:9].afind()) == len(await sheet[9:1].afind()) == len(sheet[1:-1].find()) == len(await sheet[-1:1].afind()) == len(await sheet[-9:9].afind()) == len(await sheet[9:-9].afind()) == 9
    assert len(await sheet[-1:-9].afind()) == len(await sheet[-9:-1].afind()) == 9
    assert len(await sheet.afind()) == len(sheet[:9].find()) == len(await sheet[:-1].afind()) == 9

    # 限定字段
    r = await sheet['序号'][:].afind()
    assert list(r[0]) == ['序号']

    r = await sheet['姓名', '成绩']['序号'][:].afind()
    assert list(r[0]) == ['序号']

    r = await sheet['姓名', '成绩']['序号'][None][:].afind()
    assert list(r[0]) == ['_id', '姓名', '序号', '幸运数字', '成绩']

    # 复杂查询
    _ = sheet[mc.年龄>=12]  # 比较
    _ = _[mc.姓名 == mf.isin('小三', '小四')]  # 被包含
    _ = _[mc.姓名 == mf.notin('十三', '十四')]  # 不被包含
    _ = _[(mc.年龄==15) | (mc.年龄>15) | (mc.年龄<15)]  # 并集
    _ = _[mc.年龄>=3][mc.年龄<100]  # 交集
    _ = _[(mc.年龄>=3) - (mc.年龄>100)]  # 差集
    _ = _[~ (mc.年龄>100)]  # 补集
    _ = _[mc.姓名 == mf.re('小')]  # 正则表达式
    _ = _[mc.幸运数字 == mf.contain_all(4, 5, 6)]  # 包含所有值
    _ = _[mc.幸运数字 == mf.contain_any(4, 5, 6)]  # 包含至少1个值
    _ = _[mc.幸运数字 == mf.contain_none(1, 2, 3)]  # 1个都不包含
    await _[:].afind()

    # 排序
    r = await sheet.order(序号=False)[:].afind()
    assert len(r) == 9
    assert r[0]['序号'] == 9

    r = await sheet.order(序号=False)[9:1:2].afind()
    assert len(r) == 5
    assert r[0]['序号'] == 1

    # 修改

    await sheet[2:5].aupdate({'性别':'女'})
    r = await sheet[mc.性别=='女'][:].afind()
    assert len(r) == 4
    assert r[0]['序号'] == 2

    r = await sheet[mc.性别!='女'][:].afind()
    assert len(r) == 5
    assert r[0]['序号'] == 1
    assert r[1]['序号'] == 6

    r = await sheet[2:5].aupdate({'性别':'女'})
    r.raw_result

    sheet[:][mc.姓名=='小六'].update({
        '姓名': 'xiaoliu',
        '年龄': mo.inc(6),
        '幸运数字': mo.push(666),
        '视力': mo.rename('眼力'),
        '籍贯': mo.delete,
        '成绩.语文': 60,
        '成绩.数学': mo.inc(-10)
    })
    r = await sheet[mc.姓名=='xiaoliu'][1].afind()
    assert r['姓名'] == 'xiaoliu' and r['序号']==6 and 666 in r['幸运数字'] and r['成绩']['语文']==60 and r['成绩']['数学']==77
    assert r['年龄'] == 6

    # 删除
    r1 = sheet[2][mc.序号>=1].delete()
    r2 = await sheet[mc.序号>=1][2:4].adelete()
    r1.raw_result
    r2.raw_result

    # 统计

    await 重置数据()
    assert await sheet.alen() == 9
    assert await sheet[mc.序号<=4].alen() == 4
    assert await db.alen() == 1
    await odm.aget_db_names()
    assert await db.aget_sheet_names() == ['学生']

    #################################################### 字段提示
    class mc2(mc):
        姓名 = 序号 = 幸运数字 = None
        class 成绩:
            语文 = 数学 = None

    mc2.成绩.语文

    r = await sheet[mc2.序号<=7][:].afind()
    assert len(r) == 7
    assert r[-1]['序号'] == 7

    r = await sheet[mc2['成绩']['语文'] == 88][:].afind()
    assert len(r) == 1
    assert r[0]['序号'] == 8

    # 迭代所有库ODM和表ODM
    
    for db in odm:
        for sheet in db:
            ...
    
    async for db in odm:
        async for sheet in db:
            ...

    # 清理测试数据
    await db.adelete_db()

asyncio.run(严格测试())


# 记录测试结果
name = 'skk.mongo'
print(f'[测试通过] {name}')
