import React, { useEffect, useState } from 'react';
import { Space, Table, Tag, Collapse, Tooltip, DatePicker, Select, Checkbox, Modal } from 'antd';
import { LABEL_MAP } from './form';
import dayjs from 'dayjs';
import { HOST } from '../constnat';
import Form from './form'






const App: React.FC = () => {
    const [goodsList, setGoodsList] = useState([]);

    const today = new Date();

    const [data, setData] = useState([])
    const [goods, setGoods] = useState('')
    const [date, setDate] = useState(dayjs(today))
    const [isShowAll, setIsShowAll] = useState(false)

    const [editItem, setEditItem] = useState<null | any>(null);

    const columns: any[] = Object.keys(LABEL_MAP).map((key) => {
        const item = {
            title: LABEL_MAP[key],
            dataIndex: key,
            key: key,
            width: 200,
            render: (value: any) => {
                return <span><Tooltip title={value}>{value}</Tooltip></span>
            }
        }
        if(key==='name') {
            (item as any).fixed = 'left'
            item.width = 100
        }
        return item
    })

    columns.push(
        {
            title: '大盘',
            key: 'market',
            dataIndex: "market",
            width: 200,
            render: (value: any) => {
                return <span><Tooltip title={value}>{value}</Tooltip></span>
            }
        }
    )

    columns.push(
        {
            title: '操作',
            key: 'action',
            dataIndex: "action",
            fixed: 'right',
            width: 80,
            render: (_: any, record: any) => (
                <Space size="middle">
                    <a onClick={() => setEditItem(record)}>编辑</a>
                </Space>
            ),
        }
    )

    const loadData = () => {
        const url = isShowAll ? `${HOST}/futures/list?date=${date.format("YYYY-MM-DD")}` : `${HOST}/futures/list?goods=${goods}`
        fetch(url)
            .then((res) => res.json())
            .then((res) => {
                setData(res)
            })
    }

    useEffect(() => {
        loadData()
    }, [goods, date, isShowAll])

    useEffect(() => {
        fetch(`${HOST}/futures/goodslist`).then((res) => {
            res.json().then((data) => {
                setGoodsList(data)
                setGoods(data[0])
            })
        })
    }, [])

    if (!goodsList.length) {
        return null
    }

    return (
        <Collapse defaultActiveKey={['1']}>
            <Collapse.Panel header="数据" key="1">
                <div style={{ display: 'flex', justifyItems: 'center', alignItems: 'center' }}>
                    <DatePicker onChange={(date) => setDate(date)} value={date} />
                    <Select disabled={isShowAll} value={goods} style={{ width: 120, margin: "0 12px" }} onChange={(value) => setGoods(value as any)} showSearch
                        filterOption={(input, option) =>
                            (option?.value ?? '').toString().toLowerCase().includes(input.toLowerCase())
                        }>
                        {
                            goodsList.map((item: any) => <Select.Option value={item}>{item}</Select.Option>)
                        }
                    </Select>
                    <Checkbox onChange={(e) => setIsShowAll(e.target.checked)} checked={isShowAll} >显示当日全部</Checkbox>
                </div>
                <Table columns={columns} dataSource={data} scroll={{ x: 1500 }} />
                <Modal title="修改" open={!!editItem} footer={null} onCancel={() => setEditItem(null)} destroyOnClose>
                    <Form initialValues={{
                        ...editItem,
                        date: dayjs(editItem?.date)
                    }} callback={() => {
                        setEditItem(null);
                        loadData();
                    }} />
                </Modal>
            </Collapse.Panel>
        </Collapse>
    )
};

export default App;