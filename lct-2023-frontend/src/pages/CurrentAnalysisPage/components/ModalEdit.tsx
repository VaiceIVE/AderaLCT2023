import { Stack, Title } from "@mantine/core";
import { useEffect, useState } from "react";
import ModalForm from "./ModalForm";

const ModalEdit = (props: {works: string[] | undefined, onClose: () => void, 
    handleSetWorks: Function
}) => {
    const [newWorks, setNewWorks] = useState<string[]>();

    useEffect(() => {
        setNewWorks(props.works);
    }, []);

    const handleAdd = () => {
        setNewWorks([...newWorks!, `Новый вид работ №${newWorks?.length! + 1}`]);
    };

    const handleDelete = (work: string) => {
        setNewWorks((item) => {
            return item?.filter(newWorks => newWorks != work);
        });
    };

    return (
        <Stack spacing={32}>
            <Title style={{textAlign: 'center'}} size="h4" color="gray.9">Редактирование</Title>
            <ModalForm 
                newWorks={newWorks}
                onCLose={props.onClose}
                handleAdd={handleAdd}
                handleDelete={handleDelete}
                handleSetWorks={props.handleSetWorks}
            />
        </Stack>
    );
};

export default ModalEdit;