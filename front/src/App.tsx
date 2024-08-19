import React, { useEffect, useState } from 'react';
import logo from './logo.svg';
import './App.css';
import { Input, Button, Alert } from 'antd';
import Layout from './layout';
import { CLIENT_ID, HOST } from './constnat';

function App() {
  const [waitingInfo, setWaitingInfo] = useState<null|{pending:number, my:number}>(null)
  useEffect(()=>{
    queryInfo()
  },[])

  const queryInfo = async () => {
    const deviceId = await CLIENT_ID()
    fetch(`${HOST}/ai/waiting?clientId=${deviceId}`).then(res => res.json()).then(data => setWaitingInfo({
      my: data.myWaitingTask,
      pending: data.beforeMyTask || 0,
    }))
  }

  const genMessage = () => {
    let message = ''
    if(waitingInfo?.my) {
      message += `您共有${waitingInfo.my}个任务待开始`
    }
    if(waitingInfo?.pending) {
      message += `，前面共有${waitingInfo.pending} 个他人任务正在等待, 预计等待${waitingInfo.pending * 20}秒`
    }
    return message
  }

  return (
    <div style={{ width: "100vw", height: "100vh" }} >
      {
        waitingInfo?.my ? (
          <Alert message={genMessage()} type="warning" showIcon/>
        ) : null
      }
      <Layout queryInfo={queryInfo}></Layout>
    </div>
  );
}

export default App;
