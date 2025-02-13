import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { HOST } from '../../constnat';
import axios from 'axios';
import ReactWordcloud from 'react-wordcloud';
import { Spin, Button, Card, Typography, Space, Divider } from 'antd';
import ReactMarkdown from 'react-markdown';
import { useTranslation } from 'react-i18next';

const { Paragraph } = Typography;

interface WordData {
    text: string;
    value: number;
}

interface Persona {
    persona: string;
    tags: Array<{ name: string; count: number }>;
}

type TranslationKeys = 
    | 'wordcloud.title'
    | 'wordcloud.generateButton'
    | 'wordcloud.personaTitle'
    | 'wordcloud.translateButton'
    | 'wordcloud.loading'
    | 'common.loading'
    | 'common.error.fetchTags'
    | 'common.error.generatePersona'
    | 'common.error.translate';

export default function WordCloud() {
    const { t } = useTranslation();
    const [words, setWords] = useState<WordData[]>([]);
    const [loading, setLoading] = useState(true);
    const [persona, setPersona] = useState<Persona | null>(null);
    const [generatingPersona, setGeneratingPersona] = useState(false);
    const [translating, setTranslating] = useState(false);
    const [translatedPersona, setTranslatedPersona] = useState<string>('');

    // Translation wrapper function with ts-ignore for type safety bypass
    const translate = (key: TranslationKeys, params?: Record<string, any>) => {
        // @ts-ignore: Suppress type checking for translation function
        return t(key, params);
    };

    // Memoize word cloud options
    const options = useMemo(() => ({
        rotations: 2,
        rotationAngles: [-90, 0] as [number, number],
        fontSizes: [20, 60] as [number, number],
        padding: 2,
        enableTooltip: false,
        deterministic: true, // Makes the layout consistent between renders
        spiral: 'archimedean' as const,
        scale: 'sqrt' as const,
        random: () => 0.5, 
    }), []); // Empty dependency array as these options never change

    // Fetch tags only once when component mounts
    useEffect(() => {
        const fetchTags = async () => {
            try {
                const response = await axios.get(`${HOST}/kl/tags/stats`);
                if (response.data.success) {
                    // Convert tag stats to word cloud format
                    const wordData = response.data.data.map((tag: { name: string; count: number }) => ({
                        text: tag.name,
                        value: tag.count
                    }));
                    setWords(wordData);
                }
            } catch (error) {
                console.error(translate('common.error.fetchTags'), error);
            } finally {
                setLoading(false);
            }
        };

        fetchTags();
        // Empty dependency array means this effect runs once on mount
    }, []);

    const handleGeneratePersona = useCallback(async () => {
        setGeneratingPersona(true);
        setTranslatedPersona(''); // Reset translation when generating new persona
        try {
            const response = await axios.get(`${HOST}/kl/tags/persona`);
            if (response.data.success) {
                setPersona(response.data.data);
            }
        } catch (error) {
            console.error(translate('common.error.generatePersona'), error);
        } finally {
            setGeneratingPersona(false);
        }
    }, []);

    const handleTranslate = useCallback(async () => {
        if (!persona) return;
        
        setTranslating(true);
        try {
            const response = await axios.post(`${HOST}/kl/translate`, {
                text: persona.persona,
                target_language: 'Chinese'
            });
            
            if (response.data.success) {
                setTranslatedPersona(response.data.translation);
            }
        } catch (error) {
            console.error(translate('common.error.translate'), error);
        } finally {
            setTranslating(false);
        }
    }, [persona]);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <Spin size="large" tip={translate('common.loading')} />
            </div>
        );
    }

    return (
        <div className="min-h-screen w-full p-8">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold">{translate('wordcloud.title')}</h1>
                    <Button 
                        type="primary"
                        onClick={handleGeneratePersona}
                        loading={generatingPersona}
                        className="bg-blue-500"
                    >
                        {translate('wordcloud.generateButton')}
                    </Button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Word Cloud Section */}
                    <div className="h-[500px] border rounded-lg shadow-lg bg-white">
                        <ReactWordcloud words={words} options={options} />
                    </div>

                    {/* Persona Section */}
                    <div className="flex flex-col space-y-4">
                        {persona && (
                            <>
                                <Card 
                                    title={(
                                        <div className="flex justify-between items-center">
                                            <span>{translate('wordcloud.personaTitle')}</span>
                                            <Button
                                                onClick={handleTranslate}
                                                loading={translating}
                                                disabled={!persona}
                                                type="default"
                                            >
                                                {translate('wordcloud.translateButton')}
                                            </Button>
                                        </div>
                                    )}
                                    className="h-[500px] overflow-y-auto"
                                >
                                    <Space direction="vertical" className="w-full">
                                        {translatedPersona && (
                                            <>
                                                <div className="prose max-w-none prose-headings:text-gray-800 prose-p:text-gray-700 prose-strong:text-gray-800 prose-li:text-gray-700">
                                                    <ReactMarkdown>{translatedPersona}</ReactMarkdown>
                                                </div>
                                                <Divider />
                                            </>
                                        )}
                                        <div className="prose max-w-none prose-headings:text-gray-800 prose-p:text-gray-700 prose-strong:text-gray-800 prose-li:text-gray-700">
                                            <ReactMarkdown>{persona.persona}</ReactMarkdown>
                                        </div>
                                    </Space>
                                </Card>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
} 