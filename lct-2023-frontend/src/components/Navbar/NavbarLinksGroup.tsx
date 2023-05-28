import { createStyles, Flex, Stack, Text } from "@mantine/core";
import { FC } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { authRoutes } from "../../utils/routes";

interface styleProps {
    location: string,
    path: string
}

const useStyles = createStyles((theme, {location, path}: styleProps) => ({
    link: {
        width: '300px',
        borderRadius: '8px',
        padding: '12px 16px',
        transition: 'all 0.2s',
        color: location === path ? theme.colors.red[7] : theme.colors.gray[8],
        svg: {
            color:  location === path ? theme.colors.red[5] : theme.colors.gray[5],
            transition: 'all 0.2s',
        },
        '&:hover': {
            borderRadius: '8px',
            background: theme.colors.red[0],
            color: theme.colors.red[7],
            svg: {
                color: theme.colors.red[5],
            },
        }
    }
}));

interface LinksProps {
    icon: React.FC<any>;
    path: string;
    title: string;
    Component: FC<{}>;
}

const NavbarLink = ({icon: Icon, path, title}: LinksProps) => {
    const location = useLocation();
    const { classes } = useStyles({location: location.pathname, path: path});
    

    return (
        <NavLink to={path}>
            <Flex align="center" gap={16} className={classes.link}>
                <Icon stroke="2" />
                <Text lh={'24px'} size="lg">{title}</Text>
            </Flex>
        </NavLink>
    );
};

const NavbarLinksGroup = () => {

    const links = authRoutes.map((link, index) => {
        if (index < 3) {
            return (
                <NavbarLink
                    {...link}
                    key={link.title}
                />
            );
        }
    });

    return (
        <nav id="nav">
            <Stack justify="center" align="center" spacing={8}>
                {links}
            </Stack>
        </nav>
    );
};

export default NavbarLinksGroup;