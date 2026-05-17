import asyncio

import asyncpg

from skk.postgre import DB, mc


async def main():
    class model(DB):    
        async def mkconn(self):
            return await asyncpg.connect(
                user = 'postgres',
                password = '123456789',
                database = '泉州市',
                host = 'localhost',
                port = 5432
            )

    # 初始化
    db = model()  # 账户db
    sheet = db['希望小学']  # 表db
    await sheet.delete()
    assert await sheet.len() == 0

    row1 = {'姓名': '小一', '年龄':11, '性别':'男', '视力':4.5, '签到日期':'2023-01-11'}
    row2 = {'姓名': '小二', '年龄':12, '性别':'男', '视力':4.6, '签到日期':'2023-01-12'}
    row3 = {'姓名': '小三', '年龄':13, '性别':'女', '视力':4.7, '签到日期':'2023-01-13'}
    row4 = {'姓名': '小四', '年龄':14, '性别':'女', '视力':4.8, '签到日期':'2023-01-14'}
    row5 = {'姓名': '小五', '年龄':15, '性别':'男', '视力':4.9, '签到日期':'2023-01-15'}
    row6 = {'姓名': '小六', '年龄':16, '性别':'女', '视力':5.0, '签到日期':'2023-01-16'}

    # 增加数据
    r1  = await sheet.insert(row1)
    r2  = await sheet.insert(row2, row3)
    r3 = await sheet.insert(row4)
    r4 = await sheet.insert(row5, row6)
    assert await sheet.len() == 6

    # 查询数据
    assert len( await sheet.select() ) == 6
    assert len( await sheet.select() ) == 6

    # 修改数据
    assert len(await  sheet[mc.年龄 == 100].select() ) == 0
    assert len(await  sheet[mc.年龄 == 200].select() ) == 0
    await sheet.update({'年龄': 100})
    assert len(await  sheet[mc.年龄 == 100].select() ) == 6
    await sheet.update({'年龄': 200})
    assert len(await  sheet[mc.年龄 == 200].select() ) == 6

    # 删除数据
    await sheet.delete()
    assert await sheet.len() == 0
    await sheet.insert(row2, row3)
    assert await sheet.len() != 0
    await sheet.delete()
    assert await sheet.len() == 0

    # 其他
    assert '希望小学' in await db.get_sheet_names()

    # 条件筛选
    ## 筛选 年龄>13、视力≧4.6、性别为女 的数据：
    await sheet[mc.年龄 > 13][mc.视力 >= 4.6][mc.性别 == '女'].select()
    await sheet[mc.年龄 > 13][mc.视力 >= 4.6][mc.性别 == '女'].update( {'年级':'初一', '爱好':'画画,跳绳'} )
    await sheet[mc.年龄 > 13][mc.视力 >= 4.6][mc.性别 == '女'].delete()

    ## 筛选 `年龄>13或视力≧4.6、姓名含有‘小’、年龄不高于15、喜欢足球但不喜欢画画` 的数据：
    await sheet[(mc.年龄>13) | (mc.视力>=4.6)][mc.姓名.re('小')][~(mc.年龄>15)][mc.爱好.re('足球') - mc.爱好.re('画画')].select( )
    await sheet[(mc.年龄>13) | (mc.视力>=4.6)][mc.姓名.re('小')][~(mc.年龄>15)][mc.爱好.re('足球') - mc.爱好.re('画画')].update( {'年级':'初三'} )
    await sheet[(mc.年龄>13) | (mc.视力>=4.6)][mc.姓名.re('小')][~(mc.年龄>15)][mc.爱好.re('足球') - mc.爱好.re('画画')].delete( )

    # 排序
    await sheet.delete()
    await sheet.insert(row1, row2, row3, row4, row5, row6)
    await sheet[mc.年级=='高一'].order(年龄=False, 姓名=True)[2:4].select()

    # 限定返回字段
    await sheet[mc.年级=='高一']['姓名','年龄'][:].select()


    # 统计
    await sheet.delete()
    await sheet.insert(row1, row2, row3, row4, row5, row6)
    assert await db.len() == 1
    assert await db.len() > 0
    assert '希望小学' in await db.get_sheet_names()
    assert await sheet.len() == 6
    assert 'id' == await sheet.get_pk()

    # 执行原生语句
    assert (await sheet.execute('select 姓名 from 希望小学 limit 1'))[0]['姓名'] == '小一'
    (await sheet.execute("update 希望小学 set 爱好='编程'"))[1]

    # 调用mysql函数
    await sheet[:].update({'备注': '签到日期'})
    await sheet[:].update({'备注': mc.签到日期})

    # 严格测试

    sheet, _ = db['希望小学', '天乐小学']

    async def 重置数据():
        await sheet[:].delete()
        assert await sheet.len() == 0
        row1 = {'姓名': '小一', '年龄':11, '签到日期':'2023-01-11'}
        row2 = {'姓名': '小二', '年龄':12, '签到日期':'2023-01-12'}
        row3 = {'姓名': '小三', '年龄':13, '签到日期':'2023-01-13'}
        row4 = {'姓名': '小四', '年龄':14, '签到日期':'2023-01-14'}
        row5 = {'姓名': '小五', '年龄':15, '签到日期':'2023-01-15'}
        row6 = {'姓名': '小六', '年龄':16, '签到日期':'2023-01-16'}
        row7 = {'姓名': '小七', '年龄':17, '签到日期':'2023-01-17'}
        row8 = {'姓名': '小八', '年龄':18, '签到日期':'2023-01-18'}
        row9 = {'姓名': '小九', '年龄':19, '签到日期':'2023-01-19'}
        await sheet.insert(*[row1, row2, row3, row4, row5, row6, row7, row8, row9])
        assert await sheet.len() == 9
    
    await 重置数据()

    # 查询
    r  = await sheet[:].select()  # 查询所有数据
    assert await sheet.len() == 9
    assert r[0]['年龄'] == 11
    r  = await sheet[3].select()  # 查询第3条数据
    assert r['年龄'] == 13
    r  = await sheet[mc.年龄>13][mc.姓名=='小五'][1].select()  # 查询年龄大于13、且姓名叫'小五'的第1条数据
    assert r['年龄'] == 15

    # 修改

    await sheet[mc.年龄>10][2:5].update({
        '视力': 5.0,
        '性别': '男',
        '爱好': '足球,篮球,画画,跳绳'
    })
    r  = await sheet[mc.视力==5.0][:].select()
    assert len(r) == 4
    assert r[0]['年龄'] == 12
    assert r[-1]['年龄'] == 15

    # 删除年龄>=15的所有数据
    await sheet[mc.年龄>=15][:].delete()
    assert await sheet.len() == 4

    # 删除年龄大于10、且喜欢足球和篮球的第2条数据
    await sheet[mc.年龄>10][mc.爱好.re('足球')][mc.爱好.re('篮球')][2].delete()
    assert await sheet.len() == 3
    assert [x['年龄'] for x in await sheet.order(id=True)[:].select()] == [11, 12, 14]

    # 删除所有数据
    await sheet[:].delete()
    assert await sheet.len() == 0

    await 重置数据()

    # 切片

    assert (await sheet[1].select())['年龄'] == 11
    assert (await sheet[2].select())['年龄'] == 12
    assert [x['年龄'] for x in await sheet[3:5].select()] == [13, 14, 15]
    
    # 限定字段
    assert frozenset(await sheet['姓名','年龄'][1].select()) == frozenset(['姓名', '年龄'])
    assert frozenset(await sheet['姓名']['年龄'][1].select()) == frozenset(['年龄'])
    assert len(await sheet[mc.年龄>11]['姓名']['*'][:].select()) > 1
    
    # 排序
    await 重置数据()
    r  = await sheet[mc.年龄>12].order(年龄=False, 姓名=True)[2:4].select()
    assert [x['年龄'] for x in r] == [18, 17, 16]
    r1  = await sheet[mc.年龄>12].order(年龄=True)[1:].select()
    r2  = await sheet[mc.年龄>12].order(年龄=False)[1:].select()
    r  = await sheet.order(年龄=True, 姓名=False).order(年龄=False)[:].select()
    assert r[0]['年龄'] == 19
    r  = await sheet.order(年龄=True, 姓名=False).order()[:].select()
    assert r[0]['年龄'] == 11

    await 重置数据()
    await sheet[2:5].update({'性别':'女'})
    r  = await sheet[mc.性别=='女'][:].select()
    assert [x['年龄'] for x in r] == [12, 13, 14, 15]
    r  = await sheet.order(id=True)[2:5].update({'性别':'男'})
    assert [x['年龄'] for x in await sheet[mc.性别=='男'][:].select()] == [12, 13, 14, 15]

    # 删除
    await 重置数据()
    await sheet[mc.年龄>13][2].delete()
    assert await sheet.len() == 8
    assert [x['年龄'] for x in await sheet.order(id=True)[:].select()] == [11, 12, 13, 14, 16, 17, 18, 19]
    await sheet[mc.年龄>13].order(id=True)[2:4].delete()
    assert await sheet.len() == 5
    assert [x['年龄'] for x in await sheet.order(id=True)[:].select()] == [11, 12, 13, 14, 19]
    r1  = await sheet[mc.年龄>13].order(id=True)[2].delete()
    assert [x['年龄'] for x in await sheet.order(id=True)[:].select()] == [11, 12, 13, 14]
    r2  = await sheet[mc.年龄>13].order(id=True)[2:4].delete()
    assert [x['年龄'] for x in await sheet.order(id=True)[:].select()] == [11, 12, 13, 14]

    await 重置数据()

    # 统计
    assert await sheet.get_pk( ) == 'id'
    len(await  sheet[mc.年龄>10].select() ) == 9
    len(await  sheet[mc.年龄>15].select() ) == 4
    assert await db.get_sheet_names( ) == ['希望小学']
    assert '希望小学'  in await db.get_sheet_names()
    assert await db.len() == 1

    await 重置数据()

    # 执行原生sql
    data = await sheet.execute('select 姓名 from 希望小学 limit 1')
    assert len(data) == 1
    assert data[0]['姓名'] == '小一'
    await 重置数据()

    # 字段提示
    class mc2(mc):
        姓名 = 年龄 = 签到日期 = 年级 = 爱好 = None
    assert [x['年龄'] for x in await sheet[mc2.年龄 > 15].select()] == [16, 17, 18, 19]

    await sheet[mc.年龄 > 5]['姓名','年龄'][mc.姓名.re('小')].order(id=False).select()
    d1  = sheet
    d2 = d1[mc.年龄 > 5]
    d3 = d2['姓名','年龄']
    d4 = d3[mc.姓名.re('小')]
    d5 = d4.order(id=False)
    await d5.select()


    await 重置数据()


    # native
    x  = sheet[mc.年龄 > 5]['姓名','年龄'][mc.姓名.re('小')].order(id=False)
    assert x._select_native() == "select 姓名, 年龄 from 希望小学 where (年龄 > 5) and (姓名 ~ '小') order by id desc"
    assert x._delete_native() == "delete from 希望小学 where (年龄 > 5) and (姓名 ~ '小')"
    assert x._update_native(dict(年龄=10, 姓名='小王')) == "update 希望小学 set 年龄=10, 姓名=小王 where (年龄 > 5) and (姓名 ~ '小')"

    # 清理测试数据
    await sheet.delete()
    assert await sheet.len() == 0


asyncio.run(main())

# 记录测试结果
name = 'skk.postgre'
print(f'[测试通过] {name}')
