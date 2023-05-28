import Wrapper from "../../components/Wrappers/Wrapper";
import Addresses from "./components/Addresses";
import MapComponent from "./components/MapComponent";

const MapsPage = () => {

    return (
        <Wrapper>
            <MapComponent/>
            <Addresses/>
        </Wrapper>
    );
};

export default MapsPage;