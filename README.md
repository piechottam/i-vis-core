<CORE> Integrated Variant Information System (I-VIS)
====================================================

I-VIS has been developed as part of the [PREDICT] project which aims to
develop software solutions for a **comPREhensive Data Integration for Cancer Treatment**.

Architecture
------------

I-VIS consists of the following python packages:
* [i-vis-core] (required): Core functionality that is shared between the API and report generation.
* [i-vis-api] (main): Creates and monitors an I-VIS API server to provide and integrate data from multiple data sources.
* [i-vis-report] (optional): WEB-interface that utilizes I-VIS API to generate reports (under heavy development).

Further reading
---------------

Check the [manual][i-vis-api-doc] for further details on:
- recommended [installation](https://i-vis-api.readthedocs.org/en/latest/installation) and [configuration](https://i-vis-api.readthedocs.org/en/latest/configuration)
  procedure
- list of [data sources](https://i-vis-api.readthedocs.org/en/latest/plugins/i-vis)


[i-vis-api-doc]: https://i-vis-api.readthedocs.org/
[i-vis-api]: https://www.github.com/piechottam/i-vis-api/
[i-vis-core]: https://www.github.com/piechottam/i-vis-core/
[i-vis-report]: https://www.github.com/piechottam/i-vis-report/
[PREDICT]: https://predict.informatik.hu-berlin.de/
