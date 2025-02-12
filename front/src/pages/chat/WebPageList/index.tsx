// components/ChatUI.js
import { useEffect, useState, useCallback, useRef } from 'react';
import axios from 'axios'; // For ES modules or frontend
import { HOST } from '../../../constnat';
import { Checkbox, Divider, List, Skeleton, Tooltip, Tag, Space } from 'antd';
import InfiniteScroll from 'react-infinite-scroll-component';
import dayjs from 'dayjs';

// Add status color mapping
const statusColorMap = {
    'WAIT_PROCESS': 'default',
    'PROCESSING': 'blue',
    'FINISH': 'green'
};

const statusTextMap = {
    'WAIT_PROCESS': '等待处理',
    'PROCESSING': '处理中',
    'FINISH': '处理完成'
};

// Global polling interval
let globalPollingInterval: NodeJS.Timer | null = null;
const POLLING_INTERVAL = 10000; // 10 seconds

// Global set to track components that need polling
const pollingComponents = new Set<() => void>();

// Start global polling if not already started
const startGlobalPolling = () => {
    if (!globalPollingInterval) {
        globalPollingInterval = setInterval(() => {
            pollingComponents.forEach(callback => callback());
        }, POLLING_INTERVAL);
    }
};

// Stop global polling if no components need it
const stopGlobalPolling = () => {
    if (globalPollingInterval && pollingComponents.size === 0) {
        clearInterval(globalPollingInterval);
        globalPollingInterval = null;
    }
};

export default function WebPageList(props: { width: number, onSelected: (ids: string[]) => void, selectedIds: string[] }) {
    const {width, selectedIds = [], onSelected} = props
    const pageSize = 10;
    const [pageNo, setPageNo] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const [data, setData] = useState<{ 
        url: string, 
        title: string; 
        summary: string, 
        id: number,
        status: 'WAIT_PROCESS' | 'PROCESSING' | 'FINISH',
        tags: string[],
        created: string
    }[]>([]);
    const [loading, setLoading] = useState(false);

    // Function to check if any item is not finished
    const hasUnfinishedItems = useCallback(() => {
        return data.some(item => item.status !== 'FINISH');
    }, [data]);

    // Get unfinished item IDs
    const getUnfinishedItemIds = useCallback(() => {
        return data
            .filter(item => item.status !== 'FINISH')
            .map(item => item.id);
    }, [data]);

    // Function to fetch status for unfinished items
    const fetchItemStatus = useCallback(async () => {
        const unfinishedIds = getUnfinishedItemIds();
        if (unfinishedIds.length === 0) {
            pollingComponents.delete(fetchItemStatus);
            stopGlobalPolling();
            return;
        }

        try {
            const response = await axios.get(`${HOST}/kl/list?pageNo=1&pageSize=${data.length}`);
            const updatedItems = response.data.data;
            
            setData(prevData => 
                prevData.map(item => {
                    const updatedItem = updatedItems.find((updated: any) => updated.id === item.id);
                    return updatedItem ? { ...item, ...updatedItem } : item;
                })
            );

            // If no more unfinished items, remove this component from polling
            if (!hasUnfinishedItems()) {
                pollingComponents.delete(fetchItemStatus);
                stopGlobalPolling();
            }
        } catch (error) {
            console.error('Error fetching item status:', error);
        }
    }, [data, hasUnfinishedItems, getUnfinishedItemIds]);

    // Setup polling when component mounts or data changes
    useEffect(() => {
        if (hasUnfinishedItems()) {
            pollingComponents.add(fetchItemStatus);
            startGlobalPolling();
        }

        // Cleanup when component unmounts
        return () => {
            pollingComponents.delete(fetchItemStatus);
            stopGlobalPolling();
        };
    }, [hasUnfinishedItems, fetchItemStatus]);

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
                                    title={
                                        <Space>
                                            <a href={item.url} className='font-bold'>{item.title}</a>
                                            <Tag color={statusColorMap[item.status]}>{statusTextMap[item.status]}</Tag>
                                            <span className="text-gray-400 text-sm">
                                                {dayjs(item.created).format('YYYY-MM-DD HH:mm')}
                                            </span>
                                        </Space>
                                    }
                                    description={
                                        <div>
                                            {width >= 600 ? (
                                                <>
                                                    <div>{item.summary}</div>
                                                    <div className="mt-2">
                                                        {item.tags.map(tag => (
                                                            <Tag key={tag} className="mr-1 mb-1">{tag}</Tag>
                                                        ))}
                                                    </div>
                                                </>
                                            ) : (
                                                <Tooltip title={
                                                    <>
                                                        <div>{item.summary}</div>
                                                        <div className="mt-2">
                                                            {item.tags.map(tag => (
                                                                <Tag key={tag} className="mr-1 mb-1">{tag}</Tag>
                                                            ))}
                                                        </div>
                                                    </>
                                                } placement='right'>
                                                    <div className='overflow-hidden text-ellipsis text-sm line-clamp-2'>
                                                        {item.summary}
                                                    </div>
                                                </Tooltip>
                                            )}
                                        </div>
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