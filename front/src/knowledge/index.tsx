import React, {useEffect, useState} from 'react';
import { LikeOutlined, MessageOutlined, StarOutlined, BaiduOutlined } from '@ant-design/icons';
import { Avatar, List, Space, message } from 'antd';
import { HOST } from '../constnat';


const App: React.FC = () => {
    const [pageList, setPageList] = useState([]);

    const querys = () => {
        fetch(HOST + '/kl/list').then((res)=> {
            res.json().then((data) => {
                setPageList(data.data)
            })
        })
    }

    useEffect(()=> {
        querys()
    }, [])

    const data = pageList.map((item: any, i) => ({
        id: item.id,
        href: item.url,
        title: item.title,
        summary: item.summary,
        text: item.text,
        avatar: `https://api.dicebear.com/7.x/miniavs/svg?seed=${i}`,
        created: item.created,
        content: item.summary || '待分析'
      }));
      
      const IconText = ({ icon, text }: { icon: React.FC; text: string }) => (
        <Space>
          {React.createElement(icon)}
          {text}
        </Space>
      );

      const refresh = () => {
        querys()
      }

      const parse = (id: string) => {
        fetch(`${HOST}/kl/parse`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id
            }),
        }).then((res) => {
            res.json().then(() => {
                refresh()
            }).catch((e)=> {
                message.error("解析失败")
            })
        })
      }

      
    return (
        <div style={{ height: "90vh", "overflow": "auto"}}>
            <List
          itemLayout="vertical"
          size="large"
          dataSource={data}
          footer={null}
          renderItem={(item) => (
            <List.Item
              key={item.title}
              actions={item.summary ? [] :[
                <a onClick={()=>parse(item.id)}>
                    <IconText icon={BaiduOutlined}  text="分析" key="list-vertical-star-o" />
                </a>
              ]}
              extra={
                <img
                  width={272}
                  alt="logo"
                  src="https://gw.alipayobjects.com/zos/rmsportal/mqaQswcyDLcXyDKnZfES.png"
                />
              }
            >
              <List.Item.Meta
                avatar={<Avatar src={item.avatar} />}
                title={<a href={item.href}>{item.title}</a>}
                description={item.created}
              />
              {item.content}
            </List.Item>
          )}
        />
        </div>
      );
}

export default App;