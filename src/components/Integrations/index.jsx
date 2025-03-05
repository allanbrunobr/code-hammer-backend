async function fetchIntegrationsDetails(
  page = pagination?.page,
  integration = selectedIntegration,
  list = listIntegrations,
) {
  setIsLoadingIntegrationsDetails(true);
  setHasErrorIntegrationsDetails(false);

  try {
    const pullRequests = await getIntegrationPullRequests(integration);
    
    setIntegrationsDetails({
      name: list?.find((el) => el?.id === integration)?.name || "",
      service: list?.find((el) => el?.id === integration)?.repository,
      history: pullRequests // Use the API response directly
    });

    setIsLoadingIntegrationsDetails(false);
    setHasErrorIntegrationsDetails(false);
  } catch (error) {
    console.error("Error fetching integration details:", error);
    setHasErrorIntegrationsDetails(true);
    setIsLoadingIntegrationsDetails(false);
    toast.error(t("integrations.messages.fetchDetailsError"));
  }
} 