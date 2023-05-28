import { Stack, Title } from "@mantine/core";

type Props = {
    children?: React.ReactNode[];
};

const BlockWrapper = ({children}: Props) => {

    return (
        <Stack spacing={24}>
            <Title size="h4" color="gray.9">{children ? children[0] : <></>}</Title>
            <Stack>
                {children ? children[1] : <></>}
            </Stack>
            {children ? children[2] ? 
            <Stack>
                {children ? children[2] : <></>}
            </Stack>
            : <></> : <></>}
        </Stack>
    );
};

export default BlockWrapper;