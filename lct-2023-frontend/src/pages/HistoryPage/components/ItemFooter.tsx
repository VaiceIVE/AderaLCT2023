import { Button, Flex, Text } from "@mantine/core";
import { useNavigate } from "react-router-dom";
import { CURRENT_ANALYSIS_ROUT } from "../../../utils/const";

const ItemFooter = (props: {type: string, id: string, criterias: string[]}) => {
    const navigate = useNavigate();

    const footer = () => {
        return (
            <Flex gap={4} align="center">
                <Text size="lg" lh={'24px'} color="gray.9">Критерии:</Text>
                {props.type === 'base' ?
                    <Text size="lg" lh={'24px'} color="gray.6">-</Text>
                :
                    <Flex gap={2}>
                        {props.criterias!.map((item, index) => {
                            if (index === 2) {
                                return (
                                    <Text key={index} size="lg" lh={'24px'} color="gray.6">
                                        c {item.toString().substring(0,10)} по {item.toString().substring(25,35)}
                                    </Text>
                                )
                            } else {
                                return (
                                    <Text key={index} size="lg" lh={'24px'} color="gray.6">
                                        {item},
                                    </Text>
                                )
                            }
                        })}
                    </Flex>
                }
            </Flex>
        );
    };

    return (
        <Flex align="center" justify="space-between">
            {footer()}
            <Button
                onClick={() => navigate(CURRENT_ANALYSIS_ROUT + '/' + props.id)} 
                h={48} w={164}
                fz='lg'
                fw={400}
                style={{color: '#1C1C1C', background: 'white', 
                border: '1px solid #ADB5BD', cursor: 'pointer'}}
            >
                Смотреть
            </Button>
        </Flex>
    );
};

export default ItemFooter;