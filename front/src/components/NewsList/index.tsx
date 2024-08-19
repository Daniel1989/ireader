import React, { useEffect, useState } from 'react';
import type { FormProps } from 'antd';
import { Button, Checkbox, Form, Input, List, message } from 'antd';
import { CLIENT_ID, HOST } from '../../constnat';



const NewsList = (props:any) => {
    const { rssId, queryInfo } = props;
    const [news, setNews] = useState([
        // {
        //     aiSummary: "",
        //     aiSummaryStatus: "",
        //     link: "http://www.chinanews.com/cj/2024/08-17/10270492.shtml",
        //     summary: "中新网天津8月17日电 (记者 周亚强)京津冀低空经济产业联盟17日在天津市宝坻区北京科技大学天津学院揭牌成立，2024中国大学生飞行器设计创新大赛中部赛区选拔赛同期开赛。当天，包括低温电池生产线及配套工厂建设、京津中关村科技城低空公共航路设计整体规划等33个低空经济产业相关项目正式签约宝坻。",
        //     title: "京津冀低空经济产业联盟在天津成立"
        // }
    ]);


    const queryNews = async () => {
        const deviceId = await CLIENT_ID()
        fetch(`${HOST}/rss/detail?id=${rssId}&clientId=${deviceId}`).then((res)=>{
            res.json().then((data)=>{
                setNews(data.data)
                const waitingList = data.data.filter((item:any)=> item.aiSummaryStatus === 'waiting' || item.aiSummaryStatus === 'starting');
                if(waitingList.length) {
                    setTimeout(()=> {
                        queryNews();
                        queryInfo();
                    }, 5000)
                }
            })
        })
    }


    useEffect(()=>{
        if(rssId) {
            queryNews()
        }
    }, [rssId])

    



    const renderItem = (item:any) => {
        return (
            <List.Item.Meta
                title={<a href={item.link}  target='_blank'>{item.title}</a>}
                description={renderAction(item)}
            />
        )
            
    }

    const createTask = async (link: string) => {
        const deviceId = await CLIENT_ID()
        fetch(`${HOST}/ai/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: link,
                clientId: deviceId
            }),
        }).then((res) => {
            res.json().then((data) => {
                if (data.success) {
                    queryNews()
                } else {
                    message.error(data.errorMsg)
                }
            })
        })

    }

    const renderAction = (item:any) => {
        const { aiSummary, aiSummaryStatus } = item;
        if(aiSummaryStatus === 'starting') {
            return <div>AI正在阅读中...</div>
        } else if(aiSummaryStatus === 'failed') {
            return <div>AI思维混乱了...<span onClick={()=>createTask(item.link)}style={{color: "#1677ff", cursor: 'pointer'}}>&nbsp;点我&nbsp;</span>让AI重新阅读</div>
        } else if(aiSummaryStatus && aiSummaryStatus !== 'finish') {
            return <div>AI正在阅读其他文章，请耐心等待...</div>
        } 
        if(aiSummary) {
            return <div>{aiSummary}</div>
        } else {
            return <div>AI暂未阅读此新闻，<span onClick={()=>createTask(item.link)}style={{color: "#1677ff", cursor: 'pointer'}}>&nbsp;点我&nbsp;</span>让AI帮我阅读</div>
        }
    }
    return (
        <List
        size="large"
        header={null}
        footer={null}
        bordered
        dataSource={news}
        renderItem={(item:any) => <List.Item>{renderItem(item)}</List.Item>}
        />
    );
}


export default NewsList;