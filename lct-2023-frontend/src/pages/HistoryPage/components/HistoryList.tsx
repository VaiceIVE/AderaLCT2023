import { Flex, Stack, Title, Text, Image } from "@mantine/core";
import { useContext, useEffect } from "react";
import { Context } from "../../../main";
import HistoryServices from "../../../services/HistoryServices";
import sad from '../../../assets/sad.png';
import HistoryItem from "./HistoryItem";
import { observer } from "mobx-react-lite";

const HistoryList = () => {
    const { HStore } = useContext(Context);

    useEffect(() => {
        let isCancelled = false;
        try {
            HistoryServices.fetchHistory().then((response) => {
                if (!isCancelled) { 
                    HStore.setHistory(response.data.sort((a, b) => a.date > b.date ? -1 : 1));
                }
            });
        } catch (e) {
            console.log(e);
        };

        return () => {
            isCancelled = true;
        }
    }, []);

    return (
        <div>
            {HStore.history?.length != 0 ?
            <div>
                {HStore.history &&
                <Stack spacing={8}>
                    {HStore.history!.map((item, index) => (
                        <HistoryItem {...item} key={index}/>
                    ))}
                </Stack>}
            </div>
            : 
                <Flex  justify="center" align="center">
                    <Stack spacing={8} align="center">
                        <Image src={sad} w={600} h={338}/>
                        <Title size="h3" color="gray.9">В истории пока что пусто :(</Title>
                        <Text color="gray.7" size="lg" lh={'24px'} w={550} align="center">
                            Сделайте свой первый анализ, чтобы в истории появились результаты всех ваших операций!
                        </Text>
                    </Stack>
                </Flex>
            }
        </div>
    );
};

export default observer(HistoryList);