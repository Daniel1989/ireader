// components/ChatUI.js
import { useEffect, useRef, useState } from 'react';
import axios from 'axios'; // For ES modules or frontend
import { HOST } from '../../../constnat';
import { Checkbox, List, Tooltip } from 'antd';

export default function WebPageList(props: {width: number}) {
    const width = props.width
    const [pageSize, setPageSize] = useState(10);
    const [data, setData] = useState<{ url: string, title: string; summary: string }[]>([]);

    useEffect(() => {
        axios.get(`${HOST}/kl/list`)
            .then(response => {
                setData(response.data.data);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }, [])



    return (
        <div className="max-h-[100vh] overflow-scroll">
            <List
                itemLayout="horizontal"
                dataSource={data}
                className='p-6'
                renderItem={(item, index) => (
                    <List.Item>
                        <>
                            <Checkbox className='mr-2 self-start' />
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
        </div>
    );
}