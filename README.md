# VESPER
A Real-time Processing Framework for Vehicle Perception Augmentation

## Abstract
With today’s intelligent vehicles, there are a variety of information-rich sensors, both on and off-board, that can stream data to assist drivers. In the future, we imagine physical infrastructure capable of sensing and communicating data to vehicles to improve a driver’s awareness on the road. To process this data and present information to the driver in real-time, we introduce VESPER, a real-time processing framework and online scheduling algorithm designed to exploit distributed devices that are connected via wireless links. A significant feature of the VESPER algorithm is its ability to navigate the trade-off between accuracy and computational complexity of modern machine learning tools by adapting the workload, while still satisfying latency and throughput requirements. We refer to this capability as polymorphic computing. VESPER also scales opportunistically to leverage the computational resources of external devices. We evaluate VESPER on an image-processing pipeline and demonstrate that it outperforms offloading schemes based on static workloads.

This work has been accepted into [IECCO 2019](https://infocom2019.ieee-infocom.org/workshop-integrating-edge-computing-caching-and-offloading-next-generation-networks), the 3​rd​ International Workshop on Integrating Edge Computing, Caching, and Offloading in Next Generation Networks held at INFOCOM in Paris, France. Please see the [docs](docs) folder for the publication.


## License
VESPER is made available under a permissive license - please see [LICENSE](LICENSE.txt) for details.
