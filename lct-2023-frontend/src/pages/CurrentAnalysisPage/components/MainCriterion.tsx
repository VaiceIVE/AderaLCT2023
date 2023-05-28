import { Stack, Text } from "@mantine/core";

const MainCriterion = () => {

    return (
        <Stack spacing={16}>
            <Text color="gray.5" size="md" lh={'20px'}>Обязательные</Text>
            <Stack spacing={8}>
                <Text color="gray.9" lh={'24px'} size="lg">Частота обращения</Text>
                <Text color="gray.9" lh={'24px'} size="lg">Прошлые работы на объекте</Text>
                <Text color="gray.9" lh={'24px'} size="lg">Год постройки МКД</Text>
            </Stack>
        </Stack>
    );
}

export default MainCriterion;