import { Context } from "../../main";
import { Button, createStyles, Flex, Image, PasswordInput, Radio, Stack, Text, TextInput, Title } from "@mantine/core";
import { observer } from "mobx-react-lite";
import { FC, useContext, useState } from "react";
import loginSmall from '../../assets/login-img-small.png';
import loginBig from '../../assets/login-img-big.png';
import { NavLink, useLocation, useNavigate } from "react-router-dom";

const useStyles = createStyles((_theme, location: string) => ({
    wrapper: {
        width: '100vw',
        height: '100vh',
        background: '#1F1F1F'
    },
    card: {
        width: "964px",
        height: location==='/login' ? '538px' : '594px',
        borderRadius: '32px'
    },
    form: {
        background: 'white',
        width: '464px',
        borderRadius: ' 0px 32px 32px 0px',
        padding: '56px 32px'
    },
    input: {
        label: {
            marginBottom: '6px',
        }
    },
    radio: {
        label: {
            paddingLeft: '8px',
            fontSize: '16px'
        }
    }
}));

const AuthPage: FC = () => {
    const { UStore } = useContext(Context);
    const location = useLocation();
    const { classes } = useStyles(location.pathname);
    const navigate = useNavigate();
    const [username, setUsername] = useState<string>('');
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [role, setRole] = useState<string>('');

    const handleAuth = async () => {
        if (location.pathname === '/login') { 
            await UStore.login(email, password, role)
        } else {
            await UStore.registration(username, email, password)
        }
        if (UStore.isAuth) {
            navigate('/')
        }
    };

    if (UStore.isLoading) {
        return (
            <div>Загрузка...</div>
        );
    };

    return(
        <Flex className={classes.wrapper} align="center" justify="center">
            <Flex className={classes.card}>
                <Image 
                    radius='32px 0px 0px 32px' 
                    width={500} 
                    height={location.pathname === '/login' ? 538 : 594} 
                    src={location.pathname === '/login' ? loginSmall : loginBig}
                />
                <Stack spacing={56} className={classes.form}>
                    <Title size="h3">{location.pathname === '/login' ? 'Логин' : 'Регистрация'}</Title>
                    <Stack spacing={32}>
                        <Stack spacing={16}>
                            {location.pathname === '/login' ? 
                                <Radio.Group
                                    name="favoriteFramework"
                                    value={role}
                                    onChange={setRole}
                                >
                                    <Flex gap={24}>
                                        <Radio
                                            className={classes.radio}
                                            size="md" 
                                            color="red.7" 
                                            value="user" 
                                            label="Аналитик"
                                        />
                                        <Radio
                                            className={classes.radio}
                                            size="md" 
                                            color="red.7"
                                            value="admin" 
                                            label="Старший аналитик"
                                            style={{cursor: 'pointer'}}
                                        />
                                    </Flex>
                                </Radio.Group>
                            : <></>}
                            <TextInput
                                style={location.pathname === '/login' ? {display: 'none'} : {}}
                                placeholder="Иванов Иван"
                                label="Фамилия Имя"
                                lh={'24px'}
                                size="lg"
                                withAsterisk
                                value={username}
                                onChange={e => setUsername(e.target.value)}
                                type="text"
                                radius="0.5rem"
                                className={classes.input}
                            />
                            <TextInput
                                placeholder="aaa@yandex.ru"
                                label="Email"
                                lh={'24px'}
                                size="lg"
                                withAsterisk
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                type="email"
                                radius="0.5rem"
                                className={classes.input}
                            />
                            <PasswordInput
                                placeholder="Пароль"
                                label="Пароль"
                                lh={'24px'}
                                size="lg"
                                withAsterisk
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                radius="0.5rem"
                                className={classes.input}
                            />
                            <Button 
                                fz='lg' 
                                radius={15} 
                                w={209} h={56} 
                                color="red.7"
                                fw={400}
                                disabled={
                                    location.pathname === '/login'  
                                    ? (email && password && role) ? false : true
                                    : (email && password && username) ? false : true
                                }
                                onClick={handleAuth}
                            >
                                {location.pathname === '/login' ? 'Вход' : 'Регистрация'}
                            </Button>
                        </Stack>
                        <Flex gap={4}>
                            <Text color="gray.9" lh={'24px'} size="lg">
                                {location.pathname === '/login' ? 'Нет аккаунта?' : 'Есть аккаунт?'}
                            </Text>
                            <NavLink to={location.pathname === '/login' ? '/registration' : '/login'}>
                                <Text color="red.6" lh={'24px'} size="lg">
                                    {location.pathname === '/login' ? 'Зарегистрироваться' : 'Войти'}
                                </Text>
                            </NavLink>
                        </Flex>
                    </Stack>
                </Stack>
            </Flex>
        </Flex>
    );
};

export default observer(AuthPage);