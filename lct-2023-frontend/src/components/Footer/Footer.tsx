import { createStyles, rem, Flex, Image, Title, Stack, Text } from '@mantine/core';
import logo from '../../assets/logo.png';

const useStyles = createStyles((theme) => ({
  footer: {
    marginTop: rem(32),
  },

  inner: {
    position: 'sticky',
    bottom: 0,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    padding: '32px 32px 64px',

    [theme.fn.smallerThan('sm')]: {
      flexDirection: 'column',
    },
  },

}));

const FooterCentered = () => {
  const { classes } = useStyles();

  return (
    <div className={classes.footer}>
      <div className={classes.inner}>
        <Flex gap={32} align="center">
          <Image width={134} height={56} src={logo}/>
          <Title fw={500} size="h5" color="gray.3">© ООО “Адера”, 2023</Title>
        </Flex>
        

        <Stack spacing={16} align="flex-end">
          <Text size="md" color="gray.3">Россия, г. Омск</Text>
          <Text size="md" color="gray.3">aderateam@gmail.com</Text>
          <Text size="md" color="gray.3">@adera_team</Text>
        </Stack>
      </div>
    </div>
  );
}

export default FooterCentered;