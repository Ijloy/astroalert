"""Lunas del sistema solar: datos, historia, curiosidades y exploración.

Las imágenes son de Wikimedia Commons (NASA/JPL, dominio público).
"""
LUNAS = [
    {
        "id": "luna",
        "nombre": "Luna",
        "planeta": "Tierra",
        "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/FullMoon2010.jpg/600px-FullMoon2010.jpg",
        "datos": {
            "diametro_km": 3474,
            "distancia_km": 384400,
            "periodo_orbital_dias": 27.3,
            "temperatura_max": 127,
            "temperatura_min": -173,
            "gravedad": "1.62 m/s²",
            "atmosfera": "Prácticamente inexistente"
        },
        "historia": "La Luna es el único satélite natural de la Tierra y el quinto más grande del sistema solar. Ha sido observada por la humanidad desde el principio de los tiempos, influyendo en calendarios, mareas y culturas. Galileo Galilei fue el primero en estudiarla con telescopio en 1609.",
        "curiosidades": [
            "Es el único cuerpo extraterrestre pisado por humanos",
            "Se aleja de la Tierra 3.8 cm cada año",
            "Siempre muestra la misma cara hacia la Tierra",
            "Tiene terremotos lunares (lunamotos)"
        ],
        "exploracion": "El programa Apollo de la NASA llevó 12 astronautas a la superficie lunar entre 1969 y 1972. La misión Apollo 11 fue la primera alunizaje tripulado el 20 de julio de 1969. Actualmente el programa Artemis de NASA planea regresar humanos a la Luna."
    },
    {
        "id": "io",
        "nombre": "Io",
        "planeta": "Júpiter",
        "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Io_highest_resolution_true_color.jpg/600px-Io_highest_resolution_true_color.jpg",
        "datos": {
            "diametro_km": 3643,
            "distancia_km": 421800,
            "periodo_orbital_dias": 1.77,
            "temperatura_max": -143,
            "temperatura_min": -183,
            "gravedad": "1.796 m/s²",
            "atmosfera": "Dióxido de azufre tenue"
        },
        "historia": "Io fue descubierta por Galileo Galilei el 8 de enero de 1610, junto con Europa, Ganímedes y Calisto. Es el cuerpo geológicamente más activo del sistema solar, con más de 400 volcanes activos. Su nombre proviene de la mitología griega.",
        "curiosidades": [
            "Tiene volcanes que lanzan material a 500 km de altura",
            "Su superficie se renueva constantemente por la actividad volcánica",
            "Los colores amarillo y naranja son depósitos de azufre",
            "La gravedad de Júpiter genera mareas que calientan su interior"
        ],
        "exploracion": "Las sondas Voyager 1 y 2 la sobrevolaron en 1979 descubriendo su actividad volcánica. La sonda Galileo la estudió entre 1995 y 2003. En 2024 la sonda Juno realizó varios sobrevuelos cercanos obteniendo imágenes detalladas."
    },
    {
        "id": "europa",
        "nombre": "Europa",
        "planeta": "Júpiter",
        "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Europa-moon.jpg/600px-Europa-moon.jpg",
        "datos": {
            "diametro_km": 3122,
            "distancia_km": 671100,
            "periodo_orbital_dias": 3.55,
            "temperatura_max": -160,
            "temperatura_min": -220,
            "gravedad": "1.315 m/s²",
            "atmosfera": "Oxígeno muy tenue"
        },
        "historia": "Europa fue descubierta por Galileo Galilei en 1610. Su superficie de hielo liso con pocas cráteres sugiere que es geológicamente joven. Es considerada uno de los lugares más prometedores para buscar vida extraterrestre en el sistema solar.",
        "curiosidades": [
            "Tiene un océano de agua líquida bajo su capa de hielo",
            "El océano podría tener el doble de agua que todos los océanos de la Tierra",
            "Sus líneas rojas son fracturas en el hielo llenas de sal",
            "Podría albergar vida en su océano subsuperficial"
        ],
        "exploracion": "La misión Europa Clipper de NASA fue lanzada en octubre de 2024 y llegará a Júpiter en 2030. Realizará 49 sobrevuelos de Europa para estudiar su océano. La ESA también planea la misión JUICE para estudiar las lunas de Júpiter."
    },
    {
        "id": "ganimedes",
        "nombre": "Ganímedes",
        "planeta": "Júpiter",
        "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Ganymede_-_Galileo_spacecraft_-_PIA00081.jpg/600px-Ganymede_-_Galileo_spacecraft_-_PIA00081.jpg",
        "datos": {
            "diametro_km": 5268,
            "distancia_km": 1070400,
            "periodo_orbital_dias": 7.15,
            "temperatura_max": -113,
            "temperatura_min": -183,
            "gravedad": "1.428 m/s²",
            "atmosfera": "Oxígeno muy tenue"
        },
        "historia": "Ganímedes es la luna más grande del sistema solar, incluso mayor que el planeta Mercurio. Fue descubierta por Galileo en 1610. Es el único satélite del sistema solar con campo magnético propio, lo que genera auroras en sus polos.",
        "curiosidades": [
            "Es más grande que Mercurio pero tiene menos masa",
            "Es la única luna con magnetosfera propia",
            "Tiene auroras ultravioleta en sus polos",
            "Posiblemente tiene un océano salado bajo su superficie"
        ],
        "exploracion": "La sonda Galileo realizó varios sobrevuelos entre 1995 y 2000. La misión JUICE de la ESA, lanzada en 2023, entrará en órbita alrededor de Ganímedes en 2034 — será la primera misión en orbitar una luna que no sea la nuestra."
    },
    {
        "id": "calisto",
        "nombre": "Calisto",
        "planeta": "Júpiter",
        "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Callisto.jpg/600px-Callisto.jpg",
        "datos": {
            "diametro_km": 4821,
            "distancia_km": 1882700,
            "periodo_orbital_dias": 16.69,
            "temperatura_max": -108,
            "temperatura_min": -193,
            "gravedad": "1.235 m/s²",
            "atmosfera": "Dióxido de carbono tenue"
        },
        "historia": "Calisto fue descubierta por Galileo en 1610. Es la luna más alejada de las cuatro galileanas y tiene la superficie más antigua y craterizada del sistema solar. Su distancia de Júpiter la protege de la intensa radiación que afecta a las otras lunas.",
        "curiosidades": [
            "Tiene la superficie más craterizada del sistema solar",
            "Su superficie tiene 4 mil millones de años de antigüedad",
            "Es la luna más segura para una futura base humana en Júpiter",
            "Tiene el cráter de impacto más grande del sistema solar: Valhalla"
        ],
        "exploracion": "La sonda Galileo realizó 8 sobrevuelos entre 1996 y 2001. La misión JUICE de la ESA también estudiará Calisto durante su trayecto hacia Ganímedes. NASA ha considerado Calisto como posible base para exploración humana del sistema joviano."
    },
    {
        "id": "titan",
        "nombre": "Titán",
        "planeta": "Saturno",
        "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Titan_in_true_color.jpg/600px-Titan_in_true_color.jpg",
        "datos": {
            "diametro_km": 5150,
            "distancia_km": 1221870,
            "periodo_orbital_dias": 15.95,
            "temperatura_max": -179,
            "temperatura_min": -183,
            "gravedad": "1.352 m/s²",
            "atmosfera": "Nitrógeno y metano — más densa que la de la Tierra"
        },
        "historia": "Titán fue descubierto por el astrónomo holandés Christiaan Huygens en 1655. Es la segunda luna más grande del sistema solar y la única con una atmósfera densa. Tiene ríos, lagos y mares de metano líquido en su superficie.",
        "curiosidades": [
            "Es la única luna con atmósfera densa",
            "Tiene lagos y ríos de metano líquido",
            "Su atmósfera es más densa que la de la Tierra",
            "Un humano podría volar con alas artificiales en su superficie"
        ],
        "exploracion": "La sonda Cassini-Huygens llegó a Saturno en 2004. La sonda Huygens descendió a la superficie de Titán en 2005, siendo la primera vez que una sonda aterrizó en el sistema solar exterior. NASA planea la misión Dragonfly, un dron que volará por Titán a partir de 2034."
    },
    {
        "id": "encelado",
        "nombre": "Encélado",
        "planeta": "Saturno",
        "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Enceladus_from_Voyager.jpg/600px-Enceladus_from_Voyager.jpg",
        "datos": {
            "diametro_km": 504,
            "distancia_km": 238020,
            "periodo_orbital_dias": 1.37,
            "temperatura_max": -128,
            "temperatura_min": -240,
            "gravedad": "0.113 m/s²",
            "atmosfera": "Vapor de agua tenue"
        },
        "historia": "Encélado fue descubierto por William Herschel en 1789. Es una de las lunas más brillantes del sistema solar por su superficie de hielo puro. En 2005 la sonda Cassini descubrió géiseres de agua en su polo sur, revelando un océano bajo su superficie.",
        "curiosidades": [
            "Tiene géiseres que lanzan agua al espacio",
            "El agua de sus géiseres alimenta el anillo E de Saturno",
            "Tiene un océano de agua líquida con compuestos orgánicos",
            "Es uno de los candidatos más fuertes para albergar vida"
        ],
        "exploracion": "La sonda Cassini sobrevoló Encélado 23 veces entre 2005 y 2015, incluso atravesando sus géiseres. Los análisis revelaron hidrógeno molecular, silicio y compuestos orgánicos complejos en el agua eyectada. NASA planea la misión Enceladus Orbilander para buscar vida."
    },
    {
        "id": "triton",
        "nombre": "Tritón",
        "planeta": "Neptuno",
        "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Triton_moon_mosaic_Voyager_2_%28large%29.jpg/600px-Triton_moon_mosaic_Voyager_2_%28large%29.jpg",
        "datos": {
            "diametro_km": 2707,
            "distancia_km": 354800,
            "periodo_orbital_dias": 5.88,
            "temperatura_max": -235,
            "temperatura_min": -235,
            "gravedad": "0.779 m/s²",
            "atmosfera": "Nitrógeno muy tenue"
        },
        "historia": "Tritón fue descubierto por William Lassell en 1846, solo 17 días después del descubrimiento de Neptuno. Es la luna más fría del sistema solar y orbita en dirección contraria a la rotación de Neptuno, lo que sugiere que fue capturada del cinturón de Kuiper.",
        "curiosidades": [
            "Orbita en sentido contrario a la rotación de Neptuno",
            "Es la luna más fría conocida: -235°C",
            "Tiene géiseres de nitrógeno líquido",
            "En 3.6 mil millones de años chocará con Neptuno"
        ],
        "exploracion": "Solo la sonda Voyager 2 ha visitado Tritón, en agosto de 1989. Descubrió géiseres de nitrógeno y una superficie con pocos cráteres. NASA y ESA han propuesto misiones futuras a Neptuno que incluirían el estudio de Tritón."
    },
    {
        "id": "miranda",
        "nombre": "Miranda",
        "planeta": "Urano",
        "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Miranda.jpg/600px-Miranda.jpg",
        "datos": {
            "diametro_km": 472,
            "distancia_km": 129900,
            "periodo_orbital_dias": 1.41,
            "temperatura_max": -187,
            "temperatura_min": -223,
            "gravedad": "0.079 m/s²",
            "atmosfera": "Ninguna"
        },
        "historia": "Miranda fue descubierta por Gerard Kuiper en 1948. Es la luna más pequeña y cercana de las cinco principales de Urano. Tiene el acantilado más alto del sistema solar: Verona Rupes, con 20 km de altura — 10 veces el Everest.",
        "curiosidades": [
            "Tiene el acantilado más alto del sistema solar (20 km)",
            "Su superficie es caótica — probablemente fue destruida y se reensambló",
            "Caer desde Verona Rupes tardaría 12 minutos",
            "Tiene cañones 12 veces más profundos que el Gran Cañón"
        ],
        "exploracion": "Solo la sonda Voyager 2 ha visitado Miranda, en enero de 1986. Las imágenes revelaron una superficie sorprendentemente compleja con terrenos muy diferentes. No hay misiones planificadas actualmente para regresar a Urano."
    },
    {
        "id": "caronte",
        "nombre": "Caronte",
        "planeta": "Plutón",
        "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Charon_in_True_Color_-_High-Res.jpg/600px-Charon_in_True_Color_-_High-Res.jpg",
        "datos": {
            "diametro_km": 1212,
            "distancia_km": 19570,
            "periodo_orbital_dias": 6.39,
            "temperatura_max": -220,
            "temperatura_min": -258,
            "gravedad": "0.288 m/s²",
            "atmosfera": "Ninguna"
        },
        "historia": "Caronte fue descubierto por James Christy en 1978. Es tan grande en relación a Plutón que muchos astrónomos consideran a Plutón-Caronte un sistema binario. Su nombre proviene del barquero que transportaba almas al inframundo en la mitología griega.",
        "curiosidades": [
            "Es la mitad del tamaño de Plutón — casi un planeta doble",
            "Tiene una mancha roja polar llamada Mordor",
            "Plutón y Caronte siempre se muestran la misma cara mutuamente",
            "Tiene montañas de hielo que flotan en una llanura"
        ],
        "exploracion": "La sonda New Horizons sobrevoló el sistema Plutón-Caronte en julio de 2015, siendo la única visita. Las imágenes revelaron montañas de hielo, llanuras y la misteriosa mancha roja polar. Actualmente New Horizons viaja hacia el cinturón de Kuiper."
    },
]

def obtener_lunas():
    return [{'id': luna['id'], 'nombre': luna['nombre'], 'planeta': luna['planeta'], 'imagen': luna['imagen']} for luna in LUNAS]

def obtener_luna(luna_id):
    for luna in LUNAS:
        if luna['id'] == luna_id:
            return luna
    return None

if __name__ == '__main__':
    print(f'\n{len(LUNAS)} lunas cargadas:\n')
    for luna in LUNAS:
        print(f"  {luna['nombre']:<12}  {luna['planeta']}")
