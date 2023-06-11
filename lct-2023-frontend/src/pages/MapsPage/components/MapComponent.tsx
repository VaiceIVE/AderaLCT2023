import { Clusterer, Map, Placemark } from "@pbe/react-yandex-maps";
import axios from "axios";
import { observer } from "mobx-react-lite";
import { useContext, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Context } from "../../../main";

const MapComponent = () => {
    const location = useLocation();
    const [markers, setMarkers] = useState <{x: number, y: number, address: string, causes: string[], workname: string[]}[]>([]);
    const { MStore } = useContext(Context);

    useEffect(() => {
        if (MStore.addresses){
        for (let i = 0; i < MStore.addresses.length; i++) {
            try {
                axios.get(`https://geocode-maps.yandex.ru/1.x/?apikey=5fff5614-b0c5-4970-b75d-28aa88c46171&format=json&geocode=Москва, ${MStore.addresses[i]}`)
                .then(response => {
                    let stringArray: string[] = response.data.response.GeoObjectCollection.featureMember[0].GeoObject.Point.pos.split(' ');
                    let numberArray: number[] = [];
                    for (let j = 0; j < 2; j++) {
                        numberArray.push(+stringArray[j]);
                    };
                    setMarkers(item => [...item!, {x: numberArray[1], y: numberArray[0], 
                        address: MStore.addresses[i], causes: MStore.causes[i], workname: MStore.workname[i]}]);
                })
            } catch (error) {
                console.log(error)
            }
        }}
    }, [location]);

    return (
    <div>
        {markers ? 
        <Map
            defaultState={{
                center: [55.75, 37.57],
                zoom: 9,
                controls: ["zoomControl", "fullscreenControl"],
            }}
            modules={["control.ZoomControl", "control.FullscreenControl"]}
            width={1139} height={'100vh'}
        >
            <Clusterer
                options={{
                    preset: "islands#invertedOrangeClusterIcons",
                    groupByCoordinates: false,
                }}
            >
                {markers.map((item, index) => (
                    <Placemark
                        key={index} 
                        defaultGeometry={[item.x, item.y]}
                        modules={["geoObject.addon.hint", "geoObject.addon.balloon"]}
                        properties={{
                            hintContent: `${!item.address.indexOf('внутригородская') ? 
                            item.address.slice(item.address.indexOf(',')+1).trim() :
                            item.address}`,
                            iconContent: `${item.workname.length}`,
                            balloonContentHeader: `${!item.address.indexOf('внутригородская') ? 
                            item.address.slice(item.address.indexOf(',')+1).trim() :
                            item.address} <br/>`,
                            balloonContentBody: `${item.workname.map(work => {
                                return (`• ${work} <br/>`)
                            })}`,
                        }}
                        options={{
                            preset:
                            item.causes ? item.causes.length === 0 ? 'islands#blackCircleDotIcon' :
                            'islands#orangeCircleDotIcon' : 'islands#blackCircleDotIcon',
                            iconImageSize: [16, 16],
                        }}
                    />
                ))}
            </Clusterer>
        </Map>
        : <></>}
    </div>

    );
};

export default observer(MapComponent);