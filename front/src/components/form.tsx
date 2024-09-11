import React, { useEffect, useState } from 'react';
import type { FormProps } from 'antd';
import { Button, Checkbox, Form, Input, Collapse, Calendar, DatePicker, Select, message } from 'antd';
import dayjs from 'dayjs';
import { HOST } from '../constnat';

type FieldType = {
    name?: string;
    date?: string;
    currentTrending?: string;
    last5DaysTrending?: string;
    specialDaily?: string;
    currentBoxTop?: string;
    currentBoxBottom?: string;
    predictTrending?: string;
    predictTrendingReason?: string;
    selectedGoodsInOtherMonth?: string;
    stopLoss?: string;
    category?: string;
    categoryGoods?: string;
    whatIfAgainstTrending?: string

    market?: string
};

export const LABEL_MAP: { [key: string]: string } = {
    name: '品种名称',
    date: '交易日期',
    currentTrending: '当月趋势',
    last5DaysTrending: '5日趋势',
    specialDaily: '特殊K线',
    currentBoxTop: '箱体顶部',
    currentBoxBottom: '箱体底部',
    pcIndex: 'PC指数',
    cclTrending: '仓量变化',
    predictTrending: '预测趋势',
    predictTrendingReason: '预测原因',
    stopLoss: '止损位置',
    selectedGoodsInOtherMonth: '其他月份',
    category: '板块走势',
    categoryGoods: '板块商品',
    whatIfAgainstTrending: '反向预测'

}



const App: React.FC<{ initialValues?: any, callback?: any }> = (props: any) => {
    const [goodsList, setGoodsList] = useState([]);
    const [placeHodlerValue, setPlaceHodlerValue] = useState(null);

    const { initialValues, callback } = props
    const [form] = Form.useForm();
    const onFinishGoods: FormProps<FieldType>['onFinish'] = (values) => {
        const url = initialValues ? `${HOST}/futures/edit` : `${HOST}/futures/goods`
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...values,
                date: dayjs(values.date).format("YYYY-MM-DD")
            }),
        }).then((res) => {
            if (res.ok) {
                message.success('提交成功');
                callback && callback();
            } else {
                message.error('提交失败');
            }
        })
    };

    const onFinishPanel: FormProps<FieldType>['onFinish'] = (values) => {
        fetch(`${HOST}/futures/market`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...values,
                date: dayjs(values.date).format("YYYY-MM-DD")
            }),
        }).then((res) => {
            if (res.ok) {
                message.success('提交成功');
            } else {
                message.error('提交失败');
            }
        })
    };


    const onFill = () => {
        if (placeHodlerValue) {
            Object.keys(placeHodlerValue || {}).forEach((key) => {
                if (key !== 'name' && key !== 'date') {
                    form.setFieldValue(key, placeHodlerValue[key]);
                }
            })
        }
    };

    const onNext = () => {
        const name = form.getFieldValue('name')
        const index = goodsList.findIndex((item) => item === name);
        form.resetFields();
        form.setFieldValue('name', goodsList[index + 1]);
    };

    const today = new Date();
    const formattedDate = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

    useEffect(() => {
        fetch(`${HOST}/futures/goodslist`).then((res) => {
            res.json().then((data) => {
                setGoodsList(data)
            })
        })
    }, [])

    useEffect(() => {
        loadDetail()
    }, [goodsList])

    const loadDetail = (name?: string) => {
        fetch(`${HOST}/futures/detail?goods=${name || goodsList[0]}`).then((res) => {
            res.json().then((data) => {
                setPlaceHodlerValue(data)
            })
        })
    }

    if (!goodsList.length) {
        return null
    }

    return (
        <Collapse defaultActiveKey={['1']}>
            <Collapse.Panel header="当日数据" key="1">
                <Form
                    name="basic"
                    form={form}
                    labelCol={{ span: 8 }}
                    wrapperCol={{ span: 16 }}
                    initialValues={initialValues || {
                        name: goodsList[0],
                        date: dayjs(new Date()),
                    }}
                    onFinish={onFinishGoods}
                    autoComplete="off"
                    layout="inline"
                >
                    {
                        Object.keys(LABEL_MAP).map((key) => {
                            if (key === 'name') {
                                return (
                                    <Form.Item<FieldType>
                                        label={LABEL_MAP[key]}
                                        name={key as any}
                                        style={{ marginBottom: "8px" }}
                                        rules={[{ required: true }]}

                                    >
                                        <Select style={{ width: "190px" }} onChange={(e) => loadDetail(e)} showSearch
                                            filterOption={(input, option) =>
                                                (option?.value ?? '').toString().toLowerCase().includes(input.toLowerCase())
                                            }>
                                            {
                                                goodsList.map((item) => (
                                                    <Select.Option value={item}>{item}</Select.Option>
                                                ))
                                            }
                                        </Select>
                                    </Form.Item>
                                )
                            }
                            if (key === 'date') {
                                return (
                                    <Form.Item<FieldType>
                                        label={LABEL_MAP[key]}
                                        name={key as any}
                                        style={{ marginBottom: "8px" }}
                                        rules={[{ required: true }]}
                                    >
                                        <DatePicker style={{ width: "190px" }} />
                                    </Form.Item>
                                )
                            }
                            return (
                                <Form.Item<FieldType>
                                    label={LABEL_MAP[key]}
                                    name={key as any}
                                    style={{ marginBottom: "8px" }}
                                    rules={[{ required: true }]}
                                >
                                    <Input.TextArea placeholder={placeHodlerValue?.[key]} />
                                </Form.Item>
                            )
                        })
                    }
                    {
                        !initialValues ? null : (
                            <Form.Item<FieldType>
                                label='大盘'
                                name='market'
                                style={{ marginBottom: "8px" }}
                                rules={[{ required: true }]}
                            >
                                <Input.TextArea />
                            </Form.Item>
                        )
                    }
                    <Form.Item wrapperCol={{ offset: 8, span: 16 }} style={{ margin: "12px" }}>
                        <Button type="primary" htmlType="submit">
                            提交
                        </Button>
                        {
                            placeHodlerValue ? (
                                <Button htmlType="button" onClick={onFill} style={{ marginTop: "8px" }}>
                                    使用上一日填充
                                </Button>
                            ) : null
                        }
                        {/* <Button htmlType="button" onClick={onReset} style={{ marginTop: "8px", marginLeft: '8px' }}>
                            清空
                        </Button> */}
                        {
                            initialValues ? null : (
                                <Button htmlType="button" onClick={onNext} style={{ marginTop: "8px" }}>
                                    下一个
                                </Button>
                            )
                        }
                    </Form.Item>
                </Form>
            </Collapse.Panel>

            {
                initialValues ? null : (
                    <Collapse.Panel header="当日大盘" key="2">
                        <Form
                            name="basic"
                            labelCol={{ span: 2 }}
                            wrapperCol={{ span: 22 }}
                            autoComplete="off"
                            onFinish={onFinishPanel}
                            initialValues={{
                                date: dayjs(new Date()),
                            }}
                        >
                            <Form.Item<FieldType>
                                label='日期'
                                name='date'
                                style={{ marginBottom: "8px" }}
                                rules={[{ required: true }]}
                            >
                                <DatePicker style={{ width: "190px" }} />
                            </Form.Item>
                            <Form.Item<FieldType>
                                label="大盘走势"
                                name='market'
                                style={{ marginBottom: "8px" }}
                                rules={[{ required: true }]}
                            >
                                <Input.TextArea />
                            </Form.Item>
                            <Form.Item wrapperCol={{ offset: 8, span: 16 }} style={{ margin: "12px" }}>
                                <Button type="primary" htmlType="submit">
                                    提交
                                </Button>
                            </Form.Item>
                        </Form>
                    </Collapse.Panel>
                )
            }

        </Collapse>
    )
};

export default App;