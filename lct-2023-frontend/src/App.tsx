import { Loader, Stack } from "@mantine/core";
import { observer } from "mobx-react-lite";
import { useContext, useEffect } from "react";
import { BrowserRouter } from "react-router-dom"
import AppRouter from "./components/AppRouter"
import { Context } from "./main";
import './styles/reset.css';
import { YMaps } from "@pbe/react-yandex-maps";

const App = () => {
  const { UStore } = useContext(Context);

  useEffect(() => {
    if (localStorage.getItem('token')) {
      UStore.checkAuth();
    }
  }, []);

  if (UStore.isLoading) {
    return (
      <Stack h={"100vh"} align="center" justify="center">
        <Loader size="xl" color="red.5"/>
      </Stack>
    );
  }

  return (
    <BrowserRouter>
      <YMaps>
        <AppRouter/>
      </YMaps>
    </BrowserRouter>
  )
}

export default observer(App);
