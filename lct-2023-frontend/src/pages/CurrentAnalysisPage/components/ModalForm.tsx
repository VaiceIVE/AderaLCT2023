import { Button, Flex, Stack, TextInput, Title, useMantineTheme } from "@mantine/core";
import { IconTrashX, IconPlus } from "@tabler/icons-react";
import { useEffect, useState } from "react";

const ModalForm = (props: 
    {
        newWorks: string[] | undefined, handleAdd: Function, onCLose: () => void,
        handleDelete: Function, handleSetWorks: Function
    }
) => {

    const [workname, setWorkname] = useState<string[]>(props.newWorks!);
    const theme = useMantineTheme();

    useEffect(() => {
        setWorkname(props.newWorks!);
    }, [props.newWorks!])

    const handleSave = () => {
        props.handleSetWorks(workname);
        props.onCLose();
    };

    const handleChange = (e: any, index: number) => {
        const newWorkname = [...workname];
        newWorkname[index] = e.currentTarget.value;
        setWorkname(newWorkname);
    }

    return (
        <Stack spacing={24}>
            <Title size="h5" color="gray.9">Виды работ</Title>
            {workname &&
            <Stack spacing={8}>
                {workname.map((item, index) => (
                    <Flex key={index} gap={15} justify="space-between">
                        <TextInput
                            value={item}
                            onChange={(event) => handleChange(event, index)}
                            w={400} h={48}
                            size="lg"
                            lh={'24px'}
                        />
                        <IconTrashX
                            onClick={() => props.handleDelete(item)}
                            style={{cursor: 'pointer'}} 
                            stroke={'2'} 
                            color={theme.colors.red[7]}/>
                    </Flex>
                ))}
                <Button
                    onClick={() => props.handleAdd()}
                    h={48} w={444}
                    fz='lg'
                    fw={400}
                    style={{color: '#1C1C1C', background: 'white', 
                    border: '1px solid #ADB5BD', cursor: 'pointer'}}
                >
                    <Flex gap={8} align="center">
                        Добавить вид работ
                        <IconPlus stroke={'2'} width={16} height={16}/>
                    </Flex>
                </Button>
            </Stack>}
            <Flex gap={8} justify="space-between">
                <Button
                    w={218} h={48}
                    fz='lg'
                    fw={400}
                    style={{color: '#212529', background: 'white'}}
                    onClick={props.onCLose}
                >
                    Отменить
                </Button>
                <Button
                    onClick={() => handleSave()}
                    w={218} h={48}
                    fz='lg'
                    fw={400}
                    color="red.7"
                >
                    Сохранить изменения
                </Button>
            </Flex>
        </Stack>
    );
};

export default ModalForm;