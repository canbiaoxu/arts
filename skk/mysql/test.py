import pymysql, aiomysql, asyncio
from skk.mysql import ORM, mc, mf


async def main():

    class model(ORM):
        # 定义同步连接器
        def mkconn(self):
            return pymysql.connect(
                host = 'localhost',
                port = 3306,
                user = 'root',
                password = '123456789'
            )
        
        # 定义异步连接器
        async def amkconn(self):
            return await aiomysql.connect(
                host = 'localhost',
                port = 3306,
                user = 'root',
                password = '123456789'
            )
    
    # 初始化
    orm = model()  # 账户ORM
    db = orm['泉州市']  # 库ORM
    sheet = db['希望小学']  # 表ORM
    sheet.delete()
    assert sheet.len() == 0

    row1 = {'姓名': '小一', '年龄':11, '性别':'男', '视力':4.5, '签到日期':'2023-01-11'}
    row2 = {'姓名': '小二', '年龄':12, '性别':'男', '视力':4.6, '签到日期':'2023-01-12'}
    row3 = {'姓名': '小三', '年龄':13, '性别':'女', '视力':4.7, '签到日期':'2023-01-13'}
    row4 = {'姓名': '小四', '年龄':14, '性别':'女', '视力':4.8, '签到日期':'2023-01-14'}
    row5 = {'姓名': '小五', '年龄':15, '性别':'男', '视力':4.9, '签到日期':'2023-01-15'}
    row6 = {'姓名': '小六', '年龄':16, '性别':'女', '视力':5.0, '签到日期':'2023-01-16'}

    # 增加数据
    r1 = sheet.insert(row1)
    r2 = sheet.insert(row2, row3)
    r3 = await sheet.ainsert(row4)
    r4 = await sheet.ainsert(row5, row6)
    assert sheet.len() == 6
    for x in (r1, r2, r3, r4): assert x.lastrowid

    # 查询数据
    assert len( sheet.select() ) == 6
    assert len( await sheet.aselect() ) == 6

    # 修改数据
    assert len( sheet[mc.年龄 == 100].select() ) == 0
    assert len( sheet[mc.年龄 == 200].select() ) == 0
    sheet.update({'年龄': 100})
    assert len( sheet[mc.年龄 == 100].select() ) == 6
    await sheet.aupdate({'年龄': 200})
    assert len( sheet[mc.年龄 == 200].select() ) == 6

    # 删除数据
    sheet.delete()
    assert sheet.len() == 0
    sheet.insert(row2, row3)
    assert sheet.len() != 0
    await sheet.adelete()
    assert sheet.len() == 0

    # 其他
    assert '泉州市' in orm.get_db_names()
    assert '泉州市' in await orm.aget_db_names()
    assert '希望小学' in db.get_sheet_names()
    assert '希望小学' in await db.aget_sheet_names()

    # 条件筛选
    ## 筛选 年龄>13、视力≧4.6、性别为女 的数据：
    sheet[mc.年龄 > 13][mc.视力 >= 4.6][mc.性别 == '女'].select()
    sheet[mc.年龄 > 13][mc.视力 >= 4.6][mc.性别 == '女'].update( {'年级':'初一', '爱好':'画画,跳绳'} )
    sheet[mc.年龄 > 13][mc.视力 >= 4.6][mc.性别 == '女'].delete()

    ## 筛选 `年龄>13或视力≧4.6、姓名含有‘小’、年龄不高于15、喜欢足球但不喜欢画画` 的数据：
    sheet[(mc.年龄>13) | (mc.视力>=4.6)][mc.姓名.re('小')][~(mc.年龄>15)][mc.爱好.re('足球') - mc.爱好.re('画画')].select( )
    sheet[(mc.年龄>13) | (mc.视力>=4.6)][mc.姓名.re('小')][~(mc.年龄>15)][mc.爱好.re('足球') - mc.爱好.re('画画')].update( {'年级':'初三'} )
    sheet[(mc.年龄>13) | (mc.视力>=4.6)][mc.姓名.re('小')][~(mc.年龄>15)][mc.爱好.re('足球') - mc.爱好.re('画画')].delete( )

    # 排序
    sheet.delete()
    sheet.insert(row1, row2, row3, row4, row5, row6)
    sheet[mc.年级=='高一'].order(年龄=False, 姓名=True)[2:4].select()

    # 限定返回字段
    sheet[mc.年级=='高一']['姓名','年龄'][:].select()

    # 按主键修改
    data = {
        2: {'姓名':'xiao二', '年龄':20},
        3: {'年级':'三年级'},
        4: {'id':400, '视力':4.0}
    }
    sheet.update_by_pk(data)

    # 用自定义函数修改
    def handler(row:dict):
        row['年龄'] += 1  # 年龄统一加1岁
        if row['爱好'] == '打篮球':
            row['身高'] = 180
        elif row['爱好'] == '玩手机':
            row['视力'] = 1.8
        row['姓名'] = row['姓名'].replace('小', 'xiao')
    sheet[mc.年龄>11][:].apply(handler)  # 修改符合条件的所有数据
    sheet[mc.年龄>11][2:-2].apply(handler)  # 修改符合条件的第2条~倒数第2条
    sheet[mc.年龄>11][2].apply(handler)  # 修改符合条件的第2条数据

    # 统计
    sheet.delete()
    sheet.insert(row1, row2, row3, row4, row5, row6)
    assert orm.len() == 1
    assert await orm.alen() == 1
    assert '泉州市' in orm.get_db_names()
    assert '泉州市' in await orm.aget_db_names()
    assert db.len() > 0
    assert await db.alen() > 0
    assert '希望小学' in db.get_sheet_names()
    assert '希望小学' in await db.aget_sheet_names()
    assert sheet.len() == 6
    assert await sheet.alen() == 6
    assert 'id' == sheet.get_pk()
    assert 'id' == await sheet.aget_pk()

    # 执行原生语句
    assert sheet.execute('select 姓名 from 希望小学 limit 1')[0][0]['姓名'] == '小一'
    sheet.execute('update 希望小学 set 爱好="编程" limit 3')[1].rowcount
    sheet.executemany('insert into 希望小学(姓名, 年龄) values (%s, %s)', [('小七', 17), ('小八', 18)])[1].lastrowid

    # 调用mysql函数
    sheet[mf.year('签到日期') == 2023][:].select()
    sheet[mf.year('签到日期') == 2029][:].delete()
    sheet[mf.year('签到日期') == 2023][:].update({'性别':'成年'})
    sheet[:].update({'备注': '签到日期'})
    sheet[:].update({'备注': mc.签到日期})
    sheet[:].update({'备注': mf.year('签到日期')})

    # 严格测试

    sheet, _ = db['希望小学', '天乐小学']

    def 重置数据():
        sheet[:].delete()
        assert sheet.len() == 0
        row1 = {'姓名': '小一', '年龄':11, '签到日期':'2023-01-11'}
        row2 = {'姓名': '小二', '年龄':12, '签到日期':'2023-01-12'}
        row3 = {'姓名': '小三', '年龄':13, '签到日期':'2023-01-13'}
        row4 = {'姓名': '小四', '年龄':14, '签到日期':'2023-01-14'}
        row5 = {'姓名': '小五', '年龄':15, '签到日期':'2023-01-15'}
        row6 = {'姓名': '小六', '年龄':16, '签到日期':'2023-01-16'}
        row7 = {'姓名': '小七', '年龄':17, '签到日期':'2023-01-17'}
        row8 = {'姓名': '小八', '年龄':18, '签到日期':'2023-01-18'}
        row9 = {'姓名': '小九', '年龄':19, '签到日期':'2023-01-19'}
        sheet.insert(*[row1, row2, row3, row4, row5, row6, row7, row8, row9])
        assert sheet.len() == 9
    
    重置数据()

    # 查询
    r = sheet[:].select()  # 查询所有数据
    assert sheet.len() == 9
    assert r[0]['年龄'] == 11
    r = sheet[3].select()  # 查询第3条数据
    assert r['年龄'] == 13
    r = sheet[mc.年龄>13][mc.姓名=='小五'][1].select()  # 查询年龄大于13、且姓名叫'小五'的第1条数据
    assert r['年龄'] == 15

    # 修改

    sheet[mc.年龄>10][2:5].update({
        '视力': 5.0,
        '性别': '男',
        '爱好': '足球,篮球,画画,跳绳'
    })
    r = sheet[mc.视力==5.0][:].select()
    assert len(r) == 4
    assert r[0]['年龄'] == 12
    assert r[-1]['年龄'] == 15

    # 删除年龄>=15的所有数据
    sheet[mc.年龄>=15][:].delete()
    assert sheet.len() == 4
    assert sheet[-1].select()['年龄'] == 14

    # 删除年龄大于10、且喜欢足球和篮球的第2条数据
    sheet[mc.年龄>10][mc.爱好.re('足球')][mc.爱好.re('篮球')][2].delete()
    assert sheet.len() == 3
    assert [x['年龄'] for x in sheet[:].select()] == [11, 12, 14]

    # 删除所有数据
    sheet[:].delete()
    assert sheet.len() == 0

    重置数据()

    # 切片

    assert sheet[1].select()['年龄'] == 11
    assert sheet[-1].select()['年龄'] == 19
    assert sheet[2].select()['年龄'] == 12
    assert sheet[-2].select()['年龄'] == 18
    assert [x['年龄'] for x in sheet[3:5].select()] == [13, 14, 15]
    
    # 限定字段
    assert frozenset(sheet['姓名','年龄'][1].select()) == frozenset(['姓名', '年龄'])
    assert frozenset(sheet['姓名']['年龄'][1].select()) == frozenset(['年龄'])
    assert len(sheet[mc.年龄>11]['姓名']['*'][:].select()) > 1
    
    # 排序
    r = sheet[mc.年龄>12].order(年龄=False, 姓名=True)[2:4].select()
    assert [x['年龄'] for x in r] == [18, 17, 16]
    r1 = sheet[mc.年龄>12].order(年龄=True)[1:-1].select()
    r2 = sheet[mc.年龄>12].order(年龄=False)[-1:1].select()
    assert [x['年龄'] for x in r1] == [x['年龄'] for x in r2]
    r = sheet.order(年龄=True, 姓名=False).order(年龄=False)[:].select()
    assert r[0]['年龄'] == 19
    r = sheet.order(年龄=True, 姓名=False).order()[:].select()
    assert r[0]['年龄'] == 11

    重置数据()
    sheet[2:5].update({'性别':'女'})
    r = sheet[mc.性别=='女'][:].select()
    assert [x['年龄'] for x in r] == [12, 13, 14, 15]
    r = sheet[2:5].update({'性别':'男'})
    assert [x['年龄'] for x in sheet[mc.性别=='男'][:].select()] == [12, 13, 14, 15]

    # 删除
    sheet[mc.年龄>13][2].delete()
    assert sheet.len() == 8
    assert [x['年龄'] for x in sheet[:].select()] == [11, 12, 13, 14, 16, 17, 18, 19]
    sheet[mc.年龄>13][2:4].delete()
    assert sheet.len() == 5
    assert [x['年龄'] for x in sheet[:].select()] == [11, 12, 13, 14, 19]
    r1 = sheet[mc.年龄>13][2].delete()
    assert [x['年龄'] for x in sheet[:].select()] == [11, 12, 13, 14]
    r2 = sheet[mc.年龄>13][2:4].delete()
    assert [x['年龄'] for x in sheet[:].select()] == [11, 12, 13, 14]
    r1.rowcount
    r2.rowcount

    重置数据()

    # 统计
    assert sheet.get_pk( ) == 'id'
    len( sheet[mc.年龄>10].select() ) == 9
    len( sheet[mc.年龄>15].select() ) == 4
    assert '泉州市'  in  orm.get_db_names()
    assert db.get_sheet_names( ) == ['希望小学']
    assert '希望小学'  in  db.get_sheet_names()
    assert db.len() == 1

    # 调用mysql函数
    # 在查询、删除、修改的条件中使用
    assert len(sheet[mf.year('签到日期') == 2023][:].select()) == 9
    sheet[mf.year('签到日期') == 2029][:].delete()
    assert sheet.len() == 9
    sheet[mf.year('签到日期') == 2023][2:5].update({'性别':'女'})
    assert [x['年龄'] for x in sheet[mc.性别=='女'][:].select()] == [12, 13, 14, 15]
    # 在修改中使用
    sheet[:].update({'备注': '签到日期'})  # 修改为'签到日期'这个字符串
    assert sheet[mc.备注 == '签到日期'].len() == 9
    sheet[:].update({'备注': mc.签到日期})  # 修改为各自的'签到日期'字段的值
    assert sheet[1].select()['备注'] == '2023-01-11'
    assert sheet[-1].select()['备注'] == '2023-01-19'
    sheet[:].update({'备注': mf.year('签到日期')})  # 修改为各自的'签到日期'字段的值经year处理后的值
    assert sheet[1].select()['备注'] == '2023'
    assert sheet[-1].select()['备注'] == '2023'
    
    重置数据()

    # 执行原生sql
    data, cursor = sheet.execute('select 姓名 from 希望小学 limit 1')
    assert len(data) == 1
    assert data[0]['姓名'] == '小一'
    data, cursor = sheet.execute('update 希望小学 set 爱好="编程" limit 3')
    assert cursor.rowcount == 3
    assert [x['年龄'] for x in sheet[mc.爱好=='编程'][:].select()] == [11, 12, 13]
    data, cursor = sheet.execute("delete from 希望小学 limit 2")
    assert cursor.rowcount == 2
    assert [x['年龄'] for x in sheet.select()] == [13, 14, 15, 16, 17, 18, 19]
    sql = 'insert into 希望小学(姓名, 年龄) values (%s, %s)'
    students = [('小七', 17), ('小八', 18)]
    data, cursor = sheet.executemany(sql, students)
    cursor.lastrowid
    assert [x['年龄'] for x in sheet.select()] == [13, 14, 15, 16, 17, 18, 19, 17, 18]
    
    重置数据()

    # 字段提示
    class mc2(mc):
        姓名 = 年龄 = 签到日期 = 年级 = 爱好 = None
    assert [x['年龄'] for x in sheet[mc2.年龄 > 15].select()] == [16, 17, 18, 19]

    # 函数名提示
    class mf2(mf):
        reverse = length = lower = upper = None
    r = sheet[mf2.reverse('姓名') == '二小'].select()
    assert len(r) == 1
    assert r[0]['年龄'] == 12

    sheet[mc.年龄 > 5]['姓名','年龄'][mc.姓名.re('小')].order(id=False).select()
    d1 = sheet
    d2 = d1[mc.年龄 > 5]
    d3 = d2['姓名','年龄']
    d4 = d3[mc.姓名.re('小')]
    d5 = d4.order(id=False)
    d5.select()

    # apply
    重置数据()
    def edit_row(row:dict):
        row['年龄'] += 1  # 年龄统一加1岁
        if row['年龄'] > 15:
            row['爱好'] = '足球'
        else:
            row['爱好'] = '篮球'
        row['姓名'] = row['姓名'].replace('小', 'xiao')
    sheet[mc.年龄>11][2:-3].apply(edit_row)
    assert [x['年龄'] for x in sheet.select()] == [11, 12, 14, 15, 16, 17, 18, 18, 19]
    assert [x['爱好'] for x in sheet.select()] == [None, None, '篮球', '篮球', '足球', '足球', '足球', None, None]
    def edit_row(row:dict):
        row['姓名'] = '小明'
    assert type(sheet[mc.年龄>11][2].apply(edit_row)['data']) is dict
    assert [x['姓名'] for x in sheet.select()] == ['小一', '小二', '小明', 'xiao四', 'xiao五', 'xiao六', 'xiao七', '小八', '小九']

    # update_by_pk
    sheet.delete()
    assert sheet.len() == 0
    sheet.insert(*[
        {'id':11, '姓名': '小一', '年龄':11, '签到日期':'1'},
        {'id':12, '姓名': '小二', '年龄':12, '签到日期':'2'},
        {'id':13, '姓名': '小三', '年龄':13, '签到日期':'3'},
        {'id':14, '姓名': '小四', '年龄':14, '签到日期':'4'},
        {'id':15, '姓名': '小五', '年龄':15, '签到日期':'5'},
        {'id':16, '姓名': '小六', '年龄':16, '签到日期':'6'},
        {'id':17, '姓名': '小七', '年龄':17, '签到日期':'7'},
        {'id':18, '姓名': '小八', '年龄':18, '签到日期':'8'},
        {'id':19, '姓名': '小九', '年龄':19, '签到日期':'9'},
    ])
    assert sheet.len() == 9
    sheet.update_by_pk({
        12: dict(姓名='二', 年龄=20),
        14: dict(姓名='四'),
        16: dict(年龄=60),
        17: dict(id=700),
        18: dict(id=800, 年龄=80)
    })
    assert [x['id'] for x in sheet.order(签到日期=True).select()] == [11, 12, 13, 14, 15, 16, 700, 800, 19]
    assert [x['姓名'] for x in sheet.order(签到日期=True).select()] == ['小一', '二', '小三', '四', '小五', '小六', '小七', '小八', '小九']
    assert [x['年龄'] for x in sheet.order(签到日期=True).select()] == [11, 20, 13, 14, 15, 60, 17, 80, 19]

    # native
    x = sheet[mc.年龄 > 5]['姓名','年龄'][mc.姓名.re('小')].order(id=False)
    assert x._select_native() == '''select 姓名, 年龄 from 希望小学 where (年龄 > 5) and (姓名 regexp "小") order by id desc'''
    assert x._delete_native() == '''delete from 希望小学 where (年龄 > 5) and (姓名 regexp "小")'''
    assert x._update_native(dict(年龄=10, 姓名='小王')) == '''update 希望小学 set 年龄=10, 姓名=小王 where (年龄 > 5) and (姓名 regexp "小")'''

    # 清理测试数据
    sheet.delete()
    assert sheet.len() == 0


asyncio.run(main())

# 记录测试结果
name = 'skk.mysql'
print(f'[测试通过] {name}')
