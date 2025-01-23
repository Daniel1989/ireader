// components/ChatUI.js
import { useEffect, useState } from 'react';
import axios from 'axios'; // For ES modules or frontend
import { HOST } from '../../../constnat';
import { Checkbox, Divider, List, Skeleton, Tooltip } from 'antd';
import InfiniteScroll from 'react-infinite-scroll-component';


export default function WebPageList(props: { width: number, onSelected: (ids: string[]) => void, selectedIds: string[] }) {
    const {width, selectedIds = [], onSelected} = props
    const pageSize = 10;
    const [pageNo, setPageNo] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const [data, setData] = useState<{ url: string, title: string; summary: string, id: number }[]>([]);
    const [loading, setLoading] = useState(false);

    const loadMoreData = () => {
        if (loading) {
            return;
        }
        setLoading(true);
        axios.get(`${HOST}/kl/list?pageNo=${pageNo + 1}&pageSize=${pageSize}`)
            .then((response) => {
                setData([...data, ...response.data.data]);
                setPageNo(pageNo + 1);
                setLoading(false);
                setHasMore(response.data.hasNext);
            })
            .catch(() => {
                setLoading(false);
            });
    };

    useEffect(() => {
        loadMoreData();
    }, []);

    return (
        <div className="max-h-[100vh] overflow-scroll" id="scrollableDiv">
            <InfiniteScroll
                dataLength={data.length}
                next={loadMoreData}
                hasMore={hasMore}
                loader={<div className="flex justify-center p-10"><Skeleton active /></div>}
                endMessage={<Divider plain>It is all, nothing more 🤐</Divider>}
                scrollableTarget="scrollableDiv"
            >

                <List
                    itemLayout="horizontal"
                    dataSource={data}
                    className='p-6'
                    renderItem={(item, index) => (
                        <List.Item>
                            <>
                                <Checkbox className='mr-2 self-start' checked={selectedIds.includes(item.id.toString())} onChange={() => {
                                    if (selectedIds.includes(item.id.toString())) {
                                        onSelected(selectedIds.filter(id => id !== item.id.toString()));
                                    } else {
                                        onSelected([...selectedIds, item.id.toString()]);
                                    }
                                }}/>
                                <List.Item.Meta
                                    avatar={null}
                                    title={<><a href={item.url} className='font-bold'>{item.title}</a></>}
                                    description={
                                        width >= 600 ? item.summary : (
                                            <Tooltip title={item.summary} placement='right'><div className='overflow-hidden text-ellipsis text-sm  line-clamp-2'>{item.summary}</div></Tooltip>
                                        )
                                    }
                                />
                            </>
                        </List.Item>
                    )}
                />

            </InfiniteScroll>


        </div>
    );
}