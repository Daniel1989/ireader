import { Image, Spin, Typography } from "antd";
import { IMessage } from "./interface"
import LastReply from "./LastReply";
import { useEffect } from "react";
import { useTranslation } from 'react-i18next';

const { Link } = Typography;

type TranslationKeys = 
    | 'chat.you'
    | 'chat.thinking'
    | 'chat.assistant'
    | 'chat.similarity';

export default function Message(props: {
    message: IMessage,
    isLast: boolean
}) {
    const { t } = useTranslation();
    const { message, isLast } = props;
    const { user, text, sources = [] } = message;

    // Translation wrapper function with ts-ignore for type safety bypass
    const translate = (key: TranslationKeys, params?: Record<string, any>) => {
        // @ts-ignore: Suppress type checking for translation function
        return t(key, params);
    };

    const avatarUrlList = [
        'https://p6-official-plugin-sign.byteimg.com/tos-cn-i-5jbd59dj06/4a25e49a8442448081a9826d4e08aa28~tplv-5jbd59dj06-image.png?lk3s=8c875d0b&x-expires=1762940906&x-signature=0AaHedP8q400TFtD8JvI4KeChWI%3D',
        'https://p26-official-plugin-sign.byteimg.com/tos-cn-i-5jbd59dj06/0d9fb5d8b3994daebbdb1e4fbe989c74~tplv-5jbd59dj06-image.png?lk3s=8c875d0b&x-expires=1762941077&x-signature=GH%2FmOpCs%2B9CjDoo6xHqF%2FCa%2B6Es%3D'
    ]
    useEffect(() => {
        avatarUrlList.forEach((avatarUrl, index) => {
            fetch(avatarUrl)
                .then(response => response.blob())
                .then(blob => {
                    const reader = new FileReader();
                    reader.onloadend = function () {
                        const base64Image = reader.result;
                        localStorage.setItem("avatarBase64" + index, base64Image as string);
                    };
                    reader.readAsDataURL(blob);
                });
        })
    }, [])
    const userAvatar = localStorage.getItem("avatarBase640");
    const aiAvatar = localStorage.getItem("avatarBase641");

    const avatar = user === 'You' ? (userAvatar || avatarUrlList[0]) : (aiAvatar || avatarUrlList[1])
    if (user === 'You') {
        return (
            <div className="mt-2 flex items-start bg-gray-100 py-2 px-4 rounded fade-in">
                <div className="flex flex-col items-center">
                    <Image src={avatar} width={40} height={40} className="rounded-full" preview={false} />
                    <strong>{translate('chat.you')}</strong>
                </div>
                <span className="pl-4">{text}</span>
            </div>
        )
    } else {
        if (message.pending) {
            return (
                <div className="width-full flex items-center justify-center mt-4">
                    <Spin tip={translate('chat.thinking')} />
                </div>
            )
        }
        return (
            <div className="mt-2 flex flex-col bg-gray-300 py-2 px-4 rounded fade-in">
                <div className="flex items-start">
                    <span className="pl-2 pr-2 flex-1">{isLast ? (
                        <LastReply {...message} />
                    ) : text}</span>
                    <div className="flex flex-col items-center">
                        <Image src={avatar} width={40} height={40} className="rounded-full" preview={false} />
                        <strong>{translate('chat.assistant')}</strong>
                    </div>
                </div>
                <div className="pl-2 pr-2 flex flex-col">
                    {sources.map((source, index) => (
                        <Link 
                            className="mb-1" 
                            key={index} 
                            href={source.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                        >
                            {source.title} ({translate('chat.similarity', { value: source.similarity })})
                        </Link>
                    ))}
                </div>
            </div>
        )
    }
}