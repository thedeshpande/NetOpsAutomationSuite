/*
================================================================
NETOPS AUTOMATION SUITE
Frontend Controller
================================================================
*/


/* ================================================================
   DOM ELEMENTS
================================================================ */

const operationButtons =
    document.querySelectorAll(".operation-btn");

const siteSelect =
    document.getElementById("site");

const categorySelect =
    document.getElementById("category");

const runButton =
    document.getElementById("run-operation");

const devicePreview =
    document.getElementById("device-preview");

const deviceCount =
    document.getElementById("device-count");

const resultTable =
    document.getElementById("result-table");

const resultOperation =
    document.getElementById("result-operation");

const resultSite =
    document.getElementById("result-site");

const resultCategory =
    document.getElementById("result-category");

const executionIdElement =
    document.getElementById("execution-id");

const executionStatus =
    document.getElementById("execution-status");

const totalDevicesElement =
    document.getElementById("total-devices");

const successfulDevicesElement =
    document.getElementById("successful-devices");

const failedDevicesElement =
    document.getElementById("failed-devices");

const copyResultsButton =
    document.getElementById("copy-results");

const viewReportButton =
    document.getElementById("view-report");

const retrySection =
    document.getElementById("retry-section");

const retryButton =
    document.getElementById("retry-failed");

const cancelRetryButton =
    document.getElementById("cancel-retry");

const copyFailedButton =
    document.getElementById("copy-failed");

const retryMessage =
    document.getElementById("retry-message");

const retryQuestion =
    document.getElementById("retry-question");

const newOperationButton =
    document.getElementById("new-operation");

const resultSearch =
    document.getElementById("result-search");

const filterButtons =
    document.querySelectorAll(".filter-btn");


/* ================================================================
   APPLICATION STATE
================================================================ */

let currentOperation = "precheck";

let inventoryDevices = [];

let currentPreviewDevices = [];

let lastExecutionResult = null;

let executionRunning = false;

let retryRunning = false;

let retryAttempt = 0;

const MAX_RETRY_ATTEMPTS = 3;

let currentResultFilter = "all";


/* ================================================================
   OPERATION NAMES
================================================================ */

const operationNames = {

    precheck:
        "PRE-CHECK",

    postcheck:
        "POST-CHECK",

    backup:
        "BACKUP"

};


const operationButtonNames = {

    precheck:
        "▶ RUN PRE-CHECK",

    postcheck:
        "▶ RUN POST-CHECK",

    backup:
        "▶ RUN BACKUP"

};


/* ================================================================
   INITIALIZATION
================================================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        updateOperationUI();

        loadInventory();

    }
);


/* ================================================================
   OPERATION SELECTION
================================================================ */

operationButtons.forEach(
    (button) => {

        button.addEventListener(
            "click",
            () => {

                if (
                    executionRunning ||
                    retryRunning
                ) {
                    return;
                }


                operationButtons.forEach(
                    (item) => {

                        item.classList.remove(
                            "active"
                        );

                    }
                );


                button.classList.add(
                    "active"
                );


                currentOperation =
                    button.dataset.operation;


                updateOperationUI();

            }
        );

    }
);


/* ================================================================
   UPDATE OPERATION UI
================================================================ */

function updateOperationUI() {

    if (runButton) {

        runButton.textContent =
            operationButtonNames[
                currentOperation
            ];

    }


    if (resultOperation) {

        resultOperation.textContent =
            operationNames[
                currentOperation
            ];

    }

}


/* ================================================================
   LOAD INVENTORY
================================================================ */

async function loadInventory() {

    try {

        setLoadingState(true);


        const response =
            await fetch(
                "/api/inventory"
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                "Unable to load inventory."
            );

        }


        inventoryDevices =
            data.devices || [];


        populateSites(
            data.sites || []
        );


        populateCategories(
            data.categories || []
        );


        clearDevicePreview();


    } catch (error) {

        console.error(
            "Inventory loading failed:",
            error
        );


        showInventoryError(
            error.message
        );


    } finally {

        setLoadingState(false);

    }

}


/* ================================================================
   POPULATE SITES
================================================================ */

function populateSites(
    sites
) {

    if (!siteSelect) {
        return;
    }


    siteSelect.innerHTML = `
        <option value="">
            Select Site
        </option>

        <option value="All">
            All Sites
        </option>
    `;


    sites.forEach(
        (site) => {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                site;


            option.textContent =
                site;


            siteSelect.appendChild(
                option
            );

        }
    );

}


/* ================================================================
   POPULATE CATEGORIES
================================================================ */

function populateCategories(
    categories
) {

    if (!categorySelect) {
        return;
    }


    categorySelect.innerHTML = `
        <option value="">
            Select Category
        </option>

        <option value="All">
            All Devices
        </option>
    `;


    categories.forEach(
        (category) => {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                category;


            option.textContent =
                category;


            categorySelect.appendChild(
                option
            );

        }
    );

}


/* ================================================================
   FILTER EVENTS
================================================================ */

if (siteSelect) {

    siteSelect.addEventListener(
        "change",
        updatePreview
    );

}


if (categorySelect) {

    categorySelect.addEventListener(
        "change",
        updatePreview
    );

}


/* ================================================================
   UPDATE DEVICE PREVIEW
================================================================ */

function updatePreview() {

    if (
        !siteSelect ||
        !categorySelect
    ) {
        return;
    }


    const site =
        siteSelect.value;


    const category =
        categorySelect.value;


    if (
        !site ||
        !category
    ) {

        clearDevicePreview();

        return;

    }


    currentPreviewDevices =
        inventoryDevices.filter(
            (device) => {

                const deviceSite =
                    String(
                        device.site || ""
                    ).trim();


                const deviceCategory =
                    String(
                        device.category || ""
                    ).trim();


                const siteMatch =
                    site.toLowerCase() === "all"
                    ||
                    deviceSite.toLowerCase() ===
                    site.toLowerCase();


                const categoryMatch =
                    category.toLowerCase() === "all"
                    ||
                    deviceCategory.toLowerCase() ===
                    category.toLowerCase();


                return (
                    siteMatch &&
                    categoryMatch
                );

            }
        );


    renderDevicePreview(
        currentPreviewDevices
    );

}


/* ================================================================
   RENDER DEVICE PREVIEW
================================================================ */

function renderDevicePreview(
    devices
) {

    if (deviceCount) {

        deviceCount.textContent =
            `${devices.length} Devices`;

    }


    if (!devicePreview) {
        return;
    }


    if (!devices.length) {

        devicePreview.innerHTML = `
            <tr>

                <td
                    colspan="4"
                    class="empty-state"
                >
                    No devices found for
                    the selected scope.
                </td>

            </tr>
        `;

        return;

    }


    devicePreview.innerHTML =
        devices
            .map(
                (device) => {

                    return `
                        <tr>

                            <td>
                                ${escapeHtml(
                                    device.hostname
                                )}
                            </td>

                            <td>
                                ${escapeHtml(
                                    device.ip
                                )}
                            </td>

                            <td>
                                ${escapeHtml(
                                    device.category
                                )}
                            </td>

                            <td>
                                ${escapeHtml(
                                    device.profile
                                )}
                            </td>

                        </tr>
                    `;

                }
            )
            .join("");

}


/* ================================================================
   CLEAR DEVICE PREVIEW
================================================================ */

function clearDevicePreview() {

    currentPreviewDevices = [];


    if (deviceCount) {

        deviceCount.textContent =
            "0 Devices";

    }


    if (!devicePreview) {
        return;
    }


    devicePreview.innerHTML = `
        <tr>

            <td
                colspan="4"
                class="empty-state"
            >
                Select a site and device category
                to preview devices.
            </td>

        </tr>
    `;

}


/* ================================================================
   RUN BUTTON
================================================================ */

if (runButton) {

    runButton.addEventListener(
        "click",
        executeSelectedOperation
    );

}


/* ================================================================
   EXECUTE OPERATION
================================================================ */

async function executeSelectedOperation() {

    if (
        executionRunning ||
        retryRunning
    ) {
        return;
    }


    if (
        !siteSelect ||
        !categorySelect
    ) {

        alert(
            "Site or Category selector is missing."
        );

        return;

    }


    const site =
        siteSelect.value;


    const category =
        categorySelect.value;


    if (
        !site ||
        !category
    ) {

        alert(
            "Please select a Site and Device Category."
        );

        return;

    }


    if (!currentPreviewDevices.length) {

        alert(
            "No devices are available for the selected scope."
        );

        return;

    }


    const operationDisplay =
        operationNames[
            currentOperation
        ];


    const confirmed =
        window.confirm(
            `Proceed with ${operationDisplay}?\n\n` +
            `Site      : ${site}\n` +
            `Category  : ${category}\n` +
            `Devices   : ${currentPreviewDevices.length}`
        );


    if (!confirmed) {
        return;
    }


    executionRunning = true;

    retryAttempt = 0;


    setExecutionRunningState(
        true
    );


    showExecutionLoading(
        operationDisplay,
        site,
        category
    );


    try {

        const response =
            await fetch(
                "/api/execute",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        {
                            operation:
                                currentOperation,

                            site:
                                site,

                            category:
                                category
                        }
                    )
                }
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                "Operation execution failed."
            );

        }


        lastExecutionResult =
            data;


        renderExecutionResult(
            data
        );


        const failed =
            Number(
                data.summary?.failed || 0
            );


        if (failed > 0) {

            showRetrySection();

        } else {

            hideRetrySection();

        }


    } catch (error) {

        console.error(
            "Execution failed:",
            error
        );


        showExecutionError(
            error.message
        );


    } finally {

        executionRunning = false;


        setExecutionRunningState(
            false
        );

    }

}


/* ================================================================
   EXECUTION LOADING
================================================================ */

function showExecutionLoading(
    operation,
    site,
    category
) {

    if (resultOperation) {

        resultOperation.textContent =
            operation;

    }


    if (resultSite) {

        resultSite.textContent =
            site;

    }


    if (resultCategory) {

        resultCategory.textContent =
            category;

    }


    if (executionIdElement) {

        executionIdElement.textContent =
            "EXECUTING...";

    }


    if (executionStatus) {

        executionStatus.textContent =
            "RUNNING";

        executionStatus.className =
            "status-badge neutral";

    }


    if (totalDevicesElement) {

        totalDevicesElement.textContent =
            currentPreviewDevices.length;

    }


    if (successfulDevicesElement) {

        successfulDevicesElement.textContent =
            "—";

    }


    if (failedDevicesElement) {

        failedDevicesElement.textContent =
            "—";

    }


    if (resultTable) {

        resultTable.innerHTML = `
            <tr>

                <td
                    colspan="4"
                    class="empty-state"
                >
                    ${escapeHtml(operation)}
                    is currently running.
                    <br><br>
                    Please wait...
                </td>

            </tr>
        `;

    }


    hideRetrySection();

}


/* ================================================================
   RENDER EXECUTION RESULT
================================================================ */

function renderExecutionResult(
    data
) {

    const summary =
        data.summary || {};


    const devices =
        data.devices || [];


    const total =
        Number(
            summary.total ??
            devices.length
        );


    const successful =
        Number(
            summary.successful ??
            summary.success ??
            0
        );


    const failed =
        Number(
            summary.failed ??
            0
        );


    if (resultOperation) {

        resultOperation.textContent =
            data.operation ||
            operationNames[
                currentOperation
            ];

    }


    if (resultSite) {

        resultSite.textContent =
            data.site ||
            "—";

    }


    if (resultCategory) {

        resultCategory.textContent =
            data.category ||
            "—";

    }


    if (executionIdElement) {

        executionIdElement.textContent =
            data.execution_id ||
            "—";

    }


    if (totalDevicesElement) {

        totalDevicesElement.textContent =
            total;

    }


    if (successfulDevicesElement) {

        successfulDevicesElement.textContent =
            successful;

    }


    if (failedDevicesElement) {

        failedDevicesElement.textContent =
            failed;

    }


    if (executionStatus) {

        executionStatus.textContent =
            failed > 0
                ? "COMPLETED WITH FAILURES"
                : "SUCCESS";

        executionStatus.className =
            failed > 0
                ? "status-badge failed"
                : "status-badge success";

    }


    renderResultTable(
        devices
    );

}


/* ================================================================
   RESULT TABLE
================================================================ */

function renderResultTable(
    devices
) {

    if (!resultTable) {
        return;
    }


    let filteredDevices =
        [...devices];


    if (
        currentResultFilter ===
        "success"
    ) {

        filteredDevices =
            filteredDevices.filter(
                (device) =>
                    String(
                        device.status || ""
                    ).toUpperCase() ===
                    "SUCCESS"
            );

    }


    if (
        currentResultFilter ===
        "failed"
    ) {

        filteredDevices =
            filteredDevices.filter(
                (device) =>
                    String(
                        device.status || ""
                    ).toUpperCase() ===
                    "FAILED"
            );

    }


    const search =
        resultSearch
            ? resultSearch.value
                .trim()
                .toLowerCase()
            : "";


    if (search) {

        filteredDevices =
            filteredDevices.filter(
                (device) => {

                    const hostname =
                        String(
                            device.hostname || ""
                        ).toLowerCase();


                    const ip =
                        String(
                            device.ip || ""
                        ).toLowerCase();


                    return (
                        hostname.includes(search) ||
                        ip.includes(search)
                    );

                }
            );

    }


    if (!filteredDevices.length) {

        resultTable.innerHTML = `
            <tr>

                <td
                    colspan="4"
                    class="empty-state"
                >
                    No devices match the selected filter.
                </td>

            </tr>
        `;

        return;

    }


    resultTable.innerHTML =
        filteredDevices
            .map(
                (device) => {

                    const status =
                        String(
                            device.status || ""
                        ).toUpperCase();


                    const statusClass =
                        getStatusClass(
                            status
                        );


                    return `
                        <tr>

                            <td>
                                ${escapeHtml(
                                    device.hostname
                                )}
                            </td>

                            <td>
                                ${escapeHtml(
                                    device.ip
                                )}
                            </td>

                            <td>

                                <span
                                    class="status-badge ${statusClass}"
                                >
                                    ${escapeHtml(
                                        status
                                    )}
                                </span>

                            </td>

                            <td>
                                ${escapeHtml(
                                    device.error || ""
                                )}
                            </td>

                        </tr>
                    `;

                }
            )
            .join("");

}


/* ================================================================
   RESULT FILTERS
================================================================ */

filterButtons.forEach(
    (button) => {

        button.addEventListener(
            "click",
            () => {

                currentResultFilter =
                    button.dataset.filter;


                filterButtons.forEach(
                    (item) => {

                        item.classList.remove(
                            "active"
                        );

                    }
                );


                button.classList.add(
                    "active"
                );


                if (lastExecutionResult) {

                    renderResultTable(
                        lastExecutionResult.devices ||
                        []
                    );

                }

            }
        );

    }
);


/* ================================================================
   RESULT SEARCH
================================================================ */

if (resultSearch) {

    resultSearch.addEventListener(
        "input",
        () => {

            if (lastExecutionResult) {

                renderResultTable(
                    lastExecutionResult.devices ||
                    []
                );

            }

        }
    );

}


/* ================================================================
   RETRY HELPERS
================================================================ */

function getCurrentFailedDevices() {

    if (!lastExecutionResult) {
        return [];
    }


    return (
        lastExecutionResult.devices || []
    ).filter(
        (device) =>
            String(
                device.status || ""
            ).toUpperCase() ===
            "FAILED"
    );

}


/* ================================================================
   RETRY MESSAGE
================================================================ */

function updateRetryMessage() {

    const failedDevices =
        getCurrentFailedDevices();


    const failedCount =
        failedDevices.length;


    if (retryMessage) {

        if (retryAttempt === 0) {

            retryMessage.textContent =
                `${failedCount} device(s) failed during the operation.`;

        } else {

            retryMessage.textContent =
                `Retry Attempt ${retryAttempt} completed, ` +
                `but ${failedCount} device(s) still failed.`;

        }

    }


    if (retryQuestion) {

        if (
            retryAttempt >=
            MAX_RETRY_ATTEMPTS
        ) {

            retryQuestion.textContent =
                "Maximum retry attempts reached. " +
                "Please investigate the remaining failed device(s) manually.";

        } else {

            retryQuestion.textContent =
                "Would you like to retry the remaining " +
                "failed device(s) again?";

        }

    }


    if (retryButton) {

        if (
            retryAttempt >=
            MAX_RETRY_ATTEMPTS
        ) {

            retryButton.disabled =
                true;

            retryButton.textContent =
                "⚠ MAX RETRIES REACHED";

        } else {

            retryButton.disabled =
                false;

            retryButton.textContent =
                "↻ RETRY FAILED DEVICES";

        }

    }

}


/* ================================================================
   SHOW RETRY SECTION
================================================================ */

function showRetrySection() {

    if (retrySection) {

        retrySection.classList.remove(
            "hidden"
        );

    }


    updateRetryMessage();

}


/* ================================================================
   HIDE RETRY SECTION
================================================================ */

function hideRetrySection() {

    if (retrySection) {

        retrySection.classList.add(
            "hidden"
        );

    }

}


/* ================================================================
   RETRY FAILED DEVICES
================================================================ */

async function retryFailedDevices() {

    if (
        executionRunning ||
        retryRunning
    ) {
        return;
    }


    if (
        retryAttempt >=
        MAX_RETRY_ATTEMPTS
    ) {

        updateRetryMessage();

        return;

    }


    if (!lastExecutionResult) {

        alert(
            "No execution result is available."
        );

        return;

    }


    const failedDevices =
        getCurrentFailedDevices();


    if (!failedDevices.length) {

        hideRetrySection();

        return;

    }


    const confirmed =
        window.confirm(
            `Retry ${failedDevices.length} failed device(s)?\n\n` +
            failedDevices
                .map(
                    (device) =>
                        `${device.hostname} - ${device.ip}`
                )
                .join("\n")
        );


    if (!confirmed) {
        return;
    }


    retryRunning = true;


    if (retryButton) {

        retryButton.disabled =
            true;

        retryButton.textContent =
            "⏳ RETRYING...";

    }


    if (copyFailedButton) {

        copyFailedButton.disabled =
            true;

    }


    if (cancelRetryButton) {

        cancelRetryButton.disabled =
            true;

    }


    if (executionStatus) {

        executionStatus.textContent =
            "RETRYING";

        executionStatus.className =
            "status-badge neutral";

    }


    try {

        const response =
            await fetch(
                "/api/retry",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        {

                            operation:
                                currentOperation,

                            site:
                                lastExecutionResult.site ||
                                siteSelect.value,

                            category:
                                lastExecutionResult.category ||
                                categorySelect.value,

                            execution_id:
                                lastExecutionResult.execution_id,

                            failed_devices:
                                failedDevices.map(
                                    (device) => ({
                                        hostname:
                                            device.hostname,

                                        ip:
                                            device.ip
                                    })
                                )

                        }
                    )

                }
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                "Retry operation failed."
            );

        }


        /*
         * Retry attempt completed.
         */

        retryAttempt += 1;


        const retryResults =
            data.devices || [];


        /*
         * Map retry results by IP.
         */

        const retryMap =
            new Map(
                retryResults.map(
                    (device) => [

                        String(
                            device.ip || ""
                        ).trim(),

                        device

                    ]
                )
            );


        /*
         * Replace ONLY the devices
         * that were retried.
         */

        const finalDevices =
            (
                lastExecutionResult.devices ||
                []
            ).map(
                (device) => {

                    const ip =
                        String(
                            device.ip || ""
                        ).trim();


                    return (
                        retryMap.get(ip) ||
                        device
                    );

                }
            );


        /*
         * Recalculate final counts.
         */

        const successful =
            finalDevices.filter(
                (device) =>
                    String(
                        device.status || ""
                    ).toUpperCase() ===
                    "SUCCESS"
            ).length;


        const failed =
            finalDevices.filter(
                (device) =>
                    String(
                        device.status || ""
                    ).toUpperCase() ===
                    "FAILED"
            ).length;


        const total =
            finalDevices.length;


        /*
         * Update stored execution result.
         */

        lastExecutionResult = {

            ...lastExecutionResult,

            devices:
                finalDevices,

            summary: {

                ...(
                    lastExecutionResult.summary ||
                    {}
                ),

                total:
                    total,

                successful:
                    successful,

                failed:
                    failed

            },

            retry_attempt:
                retryAttempt

        };


        /*
         * Refresh result table.
         */

        renderExecutionResult(
            lastExecutionResult
        );


        /*
         * Everything succeeded.
         */

        if (failed === 0) {

            hideRetrySection();


            if (executionStatus) {

                executionStatus.textContent =
                    "SUCCESS";

                executionStatus.className =
                    "status-badge success";

            }

        }


        /*
         * Some devices still failed.
         */

        else {

            showRetrySection();


            if (executionStatus) {

                executionStatus.textContent =
                    "COMPLETED WITH FAILURES";

                executionStatus.className =
                    "status-badge failed";

            }

        }


    } catch (error) {

        console.error(
            "Retry execution failed:",
            error
        );


        if (executionStatus) {

            executionStatus.textContent =
                "RETRY FAILED";

            executionStatus.className =
                "status-badge failed";

        }


        alert(
            `Retry failed:\n\n${error.message}`
        );


        updateRetryMessage();

    } finally {

        retryRunning = false;


        if (copyFailedButton) {

            copyFailedButton.disabled =
                false;

        }


        if (cancelRetryButton) {

            cancelRetryButton.disabled =
                false;

        }


        updateRetryMessage();

    }

}


/* ================================================================
   RETRY BUTTON
================================================================ */

if (retryButton) {

    retryButton.addEventListener(
        "click",
        retryFailedDevices
    );

}


/* ================================================================
   CANCEL RETRY
================================================================ */

if (cancelRetryButton) {

    cancelRetryButton.addEventListener(
        "click",
        () => {

            if (retryRunning) {
                return;
            }


            hideRetrySection();

        }
    );

}


/* ================================================================
   COPY FAILED DEVICES
================================================================ */

if (copyFailedButton) {

    copyFailedButton.addEventListener(
        "click",
        async () => {

            const failedDevices =
                getCurrentFailedDevices();


            if (!failedDevices.length) {

                alert(
                    "There are no failed devices to copy."
                );

                return;

            }


            const data =
                lastExecutionResult || {};


            let text = "";


            text +=
                "NetOps Automation Suite\n";

            text +=
                "FAILED DEVICES STATUS\n";

            text +=
                "----------------------------------------\n";


            text +=
                `Site        : ${
                    data.site || ""
                }\n`;


            text +=
                `Operation   : ${
                    data.operation || ""
                }\n`;


            text +=
                `Category    : ${
                    data.category || ""
                }\n`;


            text +=
                `Execution ID: ${
                    data.execution_id || ""
                }\n`;


            text +=
                `Retry Attempt: ${
                    retryAttempt
                } / ${
                    MAX_RETRY_ATTEMPTS
                }\n`;


            text += "\n";


            text +=
                `Failed Devices: ${
                    failedDevices.length
                }\n`;


            text += "\n";


            text +=
                "Device Status\n";


            text +=
                "----------------------------------------\n";


            failedDevices.forEach(
                (device) => {

                    text +=
                        `Hostname : ${
                            device.hostname || ""
                        }\n`;


                    text +=
                        `IP       : ${
                            device.ip || ""
                        }\n`;


                    text +=
                        `Status   : ${
                            device.status ||
                            "FAILED"
                        }\n`;


                    if (device.error) {

                        text +=
                            `Reason   : ${
                                device.error
                            }\n`;

                    }


                    text += "\n";

                }
            );


            text +=
                "----------------------------------------\n";


            text +=
                "NetOps Automation Suite";


            try {

                await navigator.clipboard.writeText(
                    text.trim()
                );


                const originalText =
                    copyFailedButton.textContent;


                copyFailedButton.textContent =
                    "✓ COPIED";


                setTimeout(
                    () => {

                        copyFailedButton.textContent =
                            originalText;

                    },
                    1500
                );


            } catch (error) {

                console.error(
                    "Failed device copy failed:",
                    error
                );


                alert(
                    "Unable to copy failed device status."
                );

            }

        }
    );

}

/* ================================================================
   FORMAT FAILURE REASON FOR COPY
================================================================ */

function getCopyFailureReason(error) {

    const raw =
        String(error || "").trim();

    if (!raw) {

        return "Execution failed";

    }

    const lower =
        raw.toLowerCase();


    if (
        lower.includes(
            "authentication failed"
        ) ||

        lower.includes(
            "authentication to device failed"
        ) ||

        lower.includes(
            "auth failed"
        )
    ) {

        return "Authentication Failed";

    }


    if (
        lower.includes(
            "connection timed out"
        ) ||

        lower.includes(
            "connecttimeout"
        ) ||

        lower.includes(
            "timed out"
        )
    ) {

        return "Connection Timed Out";

    }


    if (
        lower.includes(
            "connection refused"
        ) ||

        lower.includes(
            "connectionrefused"
        )
    ) {

        return "Connection Refused";

    }


    if (
        lower.includes(
            "no route to host"
        ) ||

        lower.includes(
            "network is unreachable"
        )
    ) {

        return "Network Unreachable";

    }


    if (
        lower.includes(
            "host is down"
        ) ||

        lower.includes(
            "destination host unreachable"
        )
    ) {

        return "Device Unreachable";

    }


    /*
     * Unknown error:
     *
     * Don't copy the complete Netmiko
     * diagnostic/traceback.
     *
     * Copy only the first meaningful line.
     */

    const firstLine =
        raw
            .split(/\r?\n/)
            .map(
                (line) =>
                    line.trim()
            )
            .find(Boolean);


    return (
        firstLine ||
        "Execution Failed"
    );

}

/* ================================================================
   COPY ALL RESULTS
================================================================ */

if (copyResultsButton) {

    copyResultsButton.addEventListener(
        "click",
        async () => {

            if (!lastExecutionResult) {

                alert(
                    "No execution result is available to copy."
                );

                return;

            }


            const data =
                lastExecutionResult;


            const summary =
                data.summary || {};


            let text = "";


            text +=
                "NetOps Automation Suite\n";

            text +=
                "----------------------------------------\n";


            text +=
                `Site        : ${
                    data.site || ""
                }\n`;


            text +=
                `Operation   : ${
                    data.operation || ""
                }\n`;


            text +=
                `Category    : ${
                    data.category || ""
                }\n`;


            text +=
                `Execution ID: ${
                    data.execution_id || ""
                }\n`;


            text += "\n";


            text +=
                `Total Devices : ${
                    summary.total || 0
                }\n`;


            text +=
                `Successful    : ${
                    summary.successful ??
                    summary.success ??
                    0
                }\n`;


            text +=
                `Failed        : ${
                    summary.failed || 0
                }\n`;


            text += "\n";


            text +=
                "Device Status\n";


            text +=
                "----------------------------------------\n";


            (
                data.devices || []
            ).forEach(
                (device) => {

                    text +=
                        `${device.hostname || ""}    ` +
                        `${device.ip || ""}    ` +
                        `${device.status || ""}\n`;

                }
            );


            try {

                await navigator.clipboard.writeText(
                    text.trim()
                );


                const originalText =
                    copyResultsButton.textContent;


                copyResultsButton.textContent =
                    "✓ COPIED";


                setTimeout(
                    () => {

                        copyResultsButton.textContent =
                            originalText;

                    },
                    1500
                );


            } catch (error) {

                console.error(
                    "Copy failed:",
                    error
                );


                alert(
                    "Unable to copy results."
                );

            }

        }
    );

}


/* ================================================================
   VIEW REPORT
================================================================ */

if (viewReportButton) {

    viewReportButton.addEventListener(
        "click",
        () => {

            if (!lastExecutionResult) {

                alert(
                    "No execution report is available yet."
                );

                return;

            }


            const outputFiles =
                (
                    lastExecutionResult.devices ||
                    []
                )
                    .map(
                        (device) =>
                            device.output_file
                    )
                    .filter(
                        Boolean
                    );


            if (!outputFiles.length) {

                alert(
                    "No output file information was returned."
                );

                return;

            }


            alert(
                "Report / output files:\n\n" +
                outputFiles.join("\n")
            );

        }
    );

}


/* ================================================================
   NEW OPERATION
================================================================ */

if (newOperationButton) {

    newOperationButton.addEventListener(
        "click",
        () => {

            if (
                executionRunning ||
                retryRunning
            ) {
                return;
            }


            if (siteSelect) {

                siteSelect.value =
                    "";

            }


            if (categorySelect) {

                categorySelect.value =
                    "";

            }


            clearDevicePreview();


            lastExecutionResult =
                null;


            retryAttempt =
                0;


            currentResultFilter =
                "all";


            filterButtons.forEach(
                (button) => {

                    button.classList.remove(
                        "active"
                    );

                }
            );


            const allFilter =
                document.querySelector(
                    '.filter-btn[data-filter="all"]'
                );


            if (allFilter) {

                allFilter.classList.add(
                    "active"
                );

            }


            if (resultSearch) {

                resultSearch.value =
                    "";

            }


            if (resultOperation) {

                resultOperation.textContent =
                    operationNames[
                        currentOperation
                    ];

            }


            if (resultSite) {

                resultSite.textContent =
                    "—";

            }


            if (resultCategory) {

                resultCategory.textContent =
                    "—";

            }


            if (executionIdElement) {

                executionIdElement.textContent =
                    "—";

            }


            if (executionStatus) {

                executionStatus.textContent =
                    "READY";

                executionStatus.className =
                    "status-badge neutral";

            }


            if (totalDevicesElement) {

                totalDevicesElement.textContent =
                    "0";

            }


            if (successfulDevicesElement) {

                successfulDevicesElement.textContent =
                    "0";

            }


            if (failedDevicesElement) {

                failedDevicesElement.textContent =
                    "0";

            }


            if (resultTable) {

                resultTable.innerHTML = `
                    <tr>

                        <td
                            colspan="4"
                            class="empty-state"
                        >
                            No execution results yet.
                        </td>

                    </tr>
                `;

            }


            hideRetrySection();


            window.scrollTo(
                {
                    top: 0,
                    behavior: "smooth"
                }
            );

        }
    );

}


/* ================================================================
   EXECUTION BUTTON STATE
================================================================ */

function setExecutionRunningState(
    running
) {

    operationButtons.forEach(
        (button) => {

            button.disabled =
                running;

        }
    );


    if (siteSelect) {

        siteSelect.disabled =
            running;

    }


    if (categorySelect) {

        categorySelect.disabled =
            running;

    }


    if (runButton) {

        runButton.disabled =
            running;

    }


    if (running) {

        if (runButton) {

            runButton.textContent =
                "⏳ EXECUTING...";

        }

    } else {

        if (runButton) {

            runButton.textContent =
                operationButtonNames[
                    currentOperation
                ];

        }

    }

}


/* ================================================================
   INVENTORY LOADING STATE
================================================================ */

function setLoadingState(
    loading
) {

    if (siteSelect) {

        siteSelect.disabled =
            loading;

    }


    if (categorySelect) {

        categorySelect.disabled =
            loading;

    }


    if (loading) {

        if (deviceCount) {

            deviceCount.textContent =
                "Loading...";

        }

    }

}


/* ================================================================
   EXECUTION ERROR
================================================================ */

function showExecutionError(
    message
) {

    if (executionStatus) {

        executionStatus.textContent =
            "FAILED";

        executionStatus.className =
            "status-badge failed";

    }


    if (executionIdElement) {

        executionIdElement.textContent =
            "FAILED";

    }


    if (resultTable) {

        resultTable.innerHTML = `
            <tr>

                <td
                    colspan="4"
                    class="empty-state"
                >

                    <strong>
                        Execution Error
                    </strong>

                    <br><br>

                    ${escapeHtml(
                        message
                    )}

                </td>

            </tr>
        `;

    }


    alert(
        `Operation execution failed:\n\n${message}`
    );

}


/* ================================================================
   INVENTORY ERROR
================================================================ */

function showInventoryError(
    message
) {

    if (siteSelect) {

        siteSelect.innerHTML = `
            <option value="">
                Inventory Error
            </option>
        `;

    }


    if (categorySelect) {

        categorySelect.innerHTML = `
            <option value="">
                Inventory Error
            </option>
        `;

    }


    if (devicePreview) {

        devicePreview.innerHTML = `
            <tr>

                <td
                    colspan="4"
                    class="empty-state"
                >

                    ${escapeHtml(
                        message
                    )}

                </td>

            </tr>
        `;

    }


    if (deviceCount) {

        deviceCount.textContent =
            "Inventory Error";

    }

}


/* ================================================================
   STATUS CLASS
================================================================ */

function getStatusClass(
    status
) {

    if (
        status ===
        "SUCCESS"
    ) {

        return "success";

    }


    if (
        status ===
        "FAILED"
    ) {

        return "failed";

    }


    if (
        status ===
        "SKIPPED"
    ) {

        return "skipped";

    }


    return "neutral";

}


/* ================================================================
   HTML ESCAPE
================================================================ */

function escapeHtml(
    value
) {

    return String(
        value ?? ""
    )

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );

}