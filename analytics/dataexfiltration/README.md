# Data Exfiltration Modeling

## Goal

Implement a detection analytics for data exfiltration based on a simple model of historical network pattern.

## Application Scenario

An analyst may suspect there is a data exfiltration attack campaign going on,
but he does not have the knowledge to decide whether some traffic looks like
exfiltration and how likely it is. So he call this analytics to provide the
insights.

## Basic Idea

- Input: a list of `network-traffic` STIX SCOs in a Parquet table
- Output: the same list of SCOs in a Parquet table with two new attributes/columns
  - `x_possible_exfil_op`: this traffic may be a data retrieval from a sensitive data source or the final data exfiltration step to send it out. Need to define some data exfiltration operations and think about rules to tag traffic.
  - `x_exfil_op_probability`: providing probabilities of the operation based on the model
- Model: Uses a simple model that summarizes historical traffic from a data source and provide insights such as whether an IP in the input Parquet is visited before, and whether this IP is visited at random timing or regular timing. There is sample code to generate the model when provided a gzipped Parquet file containing a single column labelled `first_observed` and with each row containing the timestamp of the connection e.g., `2020-05-20T00:17:00.000Z`. This data can generated for testing or from actual traffic collected on the target host. The model is stored locally.
- Additional consideration: where to store the model. The model can be stored inside the container, which means the container should be periodically rebuilt, or the container reaches out to a service somewhere which stores the latest model. In the latter case, the real modeling is done somewhere else and this analytics/container only retrieves the model and does the detection. In this example, the model is stored locally.
