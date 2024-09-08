import React, { useEffect, useState } from 'react';
import { DeleteOutlined } from '@ant-design/icons';
import { Button, Layout, Menu, message, theme } from 'antd';
import AddFeeds from './components/AddFeeds';
import { CLIENT_ID, HOST } from './constnat';
import NewsList from './components/NewsList';
import Recommend from './components/recommend';
import Knowledge from './knowledge';
import { Header } from 'antd/es/layout/layout';
import { items1 } from './pages/futures';

const { Content, Sider } = Layout;


const App = (props: any) => {
  const { queryInfo } = props;
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const [rssList, setRssList] = useState([]);
  const [selectId, setSelectId] = useState('');
  const [rssType, setRssType] = useState('single');

  const [enableKnowledge, setEnableKnowledge] = useState(true);

  const deleteRss = async (id: number) => {
    const deviceId = await CLIENT_ID()
    fetch(`${HOST}/rss/delete`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id,
        clientId: deviceId
      }),
    }).then((res) => {
      res.json().then((data) => {
        if (!data.success) {
          message.error(data.errorMsg)
        } else {
          queryRss()
        }
      })
    })
  }

  const queryRss = async () => {
    const deviceId = await CLIENT_ID()
    fetch(`${HOST}/rss/list?clientId=${deviceId}&type=${rssType}`).then((res) => {
      res.json().then((data) => {
        const items = data.data.map(
          (item: any) => ({
            key: item.id + '',
            label: item.title,
            icon: <DeleteOutlined onClick={(e) => {
              deleteRss(item.id);
              e.preventDefault();
              e.stopPropagation()
            }} />,
            onClick: () => setSelectId(item.id + ''),
          }),
        );
        setRssList(items)
        if (items.length) {
          if (!selectId || !items.map((item: any) => item.key + '').includes(selectId)) {
            setSelectId(items[0].key + '')
          }
        }
      })
    })
  }

  const addFeed = async (item: any) => {
    const deviceId = await CLIENT_ID()

    fetch(`${HOST}/rss/add`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...item,
        clientId: deviceId
      }),
    }).then((res) => {
      res.json().then((data) => {
        if (data.success) {
          queryRss();
        } else {
          message.error(data.errorMsg)
        }
      })
    })
  }

  const switchType = () => {
    if (rssType === 'feeds') {
      setRssType('single')
    } else {
      setRssType('feeds')
    }
  }

  useEffect(() => {
    queryRss()
  }, [rssType])

  return (
    <Layout style={{ height: '100%' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <div className="demo-logo" />
        <Menu
          theme="dark"
          mode="horizontal"
          defaultSelectedKeys={['2']}
          items={items1}
          style={{ flex: 1, minWidth: 0 }}
        />
      </Header>

      <Layout>
        <Sider
          breakpoint="lg"
          collapsedWidth="0"
          onBreakpoint={(broken) => {
            console.log(broken);
          }}
          onCollapse={(collapsed, type) => {
            console.log(collapsed, type);
          }}
        >
          <div className="demo-logo-vertical" />
          <div style={{ display: 'flex', justifyContent: 'center', margin: '20px 0', borderBottom: '1px solid #fff' }}>
            <AddFeeds callback={queryRss} type={rssType} />
          </div>
          <div>
            {
              rssList.length ? (
                <Menu theme="dark" mode="inline" defaultSelectedKeys={[selectId]} items={rssList} />
              ) : null
            }
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', margin: '20px 0', borderTop: '1px solid #fff', flexDirection: 'column' }}>
            <Button style={{ margin: '20px 0' }} onClick={switchType}>{rssType === 'feeds' ? '使用单篇订阅' : '使用Feeds订阅'}</Button>
            <Button style={{ margin: '20px 0' }} onClick={() => setEnableKnowledge(!enableKnowledge)}>{enableKnowledge ? '关闭知识库' : '打开知识库'}</Button>
          </div>
        </Sider>
        <Content style={{ margin: '24px 16px 0' }}>
          {
            enableKnowledge ? <Knowledge /> : (
              <div
                style={{
                  padding: 24,
                  minHeight: 360,
                  height: '90%',
                  background: colorBgContainer,
                  borderRadius: borderRadiusLG,
                  overflowY: 'scroll',
                }}
              >
                {
                  !rssList.length ? (
                    <div>
                      <h4>看起来您还没有添加过rss源，请在左侧订阅一个，您也可以从下面的推荐中选择订阅。（更多优质RSS可以到这里查找<a href="https://github.com/RSS-Renaissance/awesome-blogCN-feeds" target='_blank'>awesome-blogCN-feeds</a>）</h4>
                      <Recommend callback={addFeed} />
                    </div>
                  ) : <NewsList rssId={selectId} queryInfo={queryInfo} rssType={rssType} />
                }
              </div>
            )
          }

        </Content>
      </Layout>
    </Layout>
  );
};

export default App;