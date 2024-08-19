import React from 'react';
import { Space, Table, Tag } from 'antd';
import type { TableProps } from 'antd';

interface DataType {
  key: string;
  name: string;
  address: string;
}



const data: DataType[] = [
  {
    key: '1',
    name: 'XiaoHui.com',
    address: 'https://www.xiaohui.com/rss/',
  },
];

const App = (props:any) => {
    const { callback } = props;
    const sub = async (item:any) => {
        
        callback && callback({
            title: item.name,
            url: item.address
        });
    }

    const columns: TableProps<DataType>['columns'] = [
        {
          title: '标题',
          dataIndex: 'name',
          key: 'name',
        },
        {
          title: '链接',
          dataIndex: 'address',
          key: 'address',
        },
        {
          title: '操作',
          key: 'action',
          render: (_, record) => (
            <Space size="middle">
              <a onClick={()=>sub(record)}>订阅</a>
            </Space>
          ),
        },
      ];
    return (
        <Table columns={columns} dataSource={data} />
    )
}

export default App;