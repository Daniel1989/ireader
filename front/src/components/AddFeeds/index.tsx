import React from 'react';
import type { FormProps } from 'antd';
import { Button, Checkbox, Form, Input, message } from 'antd';
import { CLIENT_ID, HOST } from '../../constnat';

type FieldType = {
    title?: string;
    url?: string;
};



const AddFeeds = (props: any) => {
    const { callback, type } = props;
    const [form] = Form.useForm();

    const onFinish: FormProps<FieldType>['onFinish'] = async (values) => {
        const deviceId = await CLIENT_ID()
        fetch(`${HOST}/rss/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...values,
                type,
                clientId: deviceId
            }),
        }).then((res) => {
            res.json().then((data) => {
                if (data.success) {
                    form.resetFields();
                    callback && callback();
                } else {
                    message.error(data.errorMsg)
                }
            })
        })
    };

    const onFinishFailed: FormProps<FieldType>['onFinishFailed'] = (errorInfo) => {
        console.log('Failed:', errorInfo);
    };
    return (
        <Form
            form={form}
            labelCol={{ span: 0 }}
            wrapperCol={{ span: 24 }}
            style={{ maxWidth: 600 }}
            initialValues={{}}
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            autoComplete="off"
        >
            <Form.Item<FieldType>
                label={null}
                name="title"
                rules={[{ required: true, message: '请输入Rss标题' }]}
            >
                <Input placeholder='请输入Rss标题' />
            </Form.Item>

            <Form.Item<FieldType>
                label={null}
                name="url"
                rules={[{ required: true, message: '请输入Rss链接' }]}
            >
                <Input placeholder='请输入Rss链接' />
            </Form.Item>

            <Form.Item wrapperCol={{ span: 16 }}>
                <Button type="primary" htmlType="submit">
                    添加订阅
                </Button>
            </Form.Item>
        </Form>
    );
}


export default AddFeeds;