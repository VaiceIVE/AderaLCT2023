import { Stack, Title, Text, Flex } from "@mantine/core";
import { useEffect, useState } from "react";

const ModalInfoBlock = (props: {stats: object, title: string}) => {
    
    const [stat, setStat] = useState <{key: string, value: any}[]>([{key: '', value: ''}]);

    useEffect(() => {
        if (props.stats) {
            for (const [key, value] of Object.entries(props.stats)) {
                setStat((item) => ([...item!, {key: key, value: value}]));
            };
        }
        
    }, [props.stats])
    
    return (
        <Stack spacing={16}>
            {stat[1] ? 
            <Title size="h5" color="gray.9">{stat[1].value === '0' ? 'Характеристики не обнаружены' 
            : props.title}</Title> : <></>}
            <Stack spacing={8}>
                {stat && stat.map((item) => (
                    item.value === '0' ? <div key={item.key} style={{display: 'none'}}></div> :
                    <Flex key={item.key} align="center" justify="space-between">
                        <Text color="gray.9" size="lg" lh={'24px'}>{item.key}</Text>
                        <Text color="gray.6" size="lg" lh={'24px'}>{item.value}</Text>
                    </Flex>
                ))}
            </Stack>
        </Stack>
    );
};

export default ModalInfoBlock;