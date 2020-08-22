function queryForm() {
    return {
        formData: {
            source: 1,
            destination: 2,
            patient_id: "",
            patient_name: "",
            patient_birth_date: "",
            study_date: "",
            modality: "",
            accession_number: "",
        },
        results: [],
        currentQueryId: null,
        noSearchYet: true,
        searchInProgress: false,
        selectAllChecked: false,
        init: function ($el, $dispatch) {
            this.form = $el;
            this.dispatch = $dispatch;
            this.connect();
        },
        connect: function () {
            const self = this;

            const wsScheme =
                window.location.protocol == "https:" ? "wss" : "ws";
            const wsUrl =
                wsScheme +
                "://" +
                window.location.host +
                "/ws/selective-transfer";

            const ws = new WebSocket(wsUrl);
            ws.onopen = function () {
                console.log("Socket is opened.");
            };
            ws.onclose = function (e) {
                console.log(
                    "Socket is closed. Reconnect will be attempted in 1 second.",
                    e.reason
                );
                setTimeout(function () {
                    self.connect(wsUrl);
                }, 1000);
            };
            ws.onmessage = function (e) {
                const data = JSON.parse(e.data);
                self.handleMessage(data);
            };
            ws.onerror = function (err) {
                console.error(
                    "Socket encountered error: ",
                    err.message,
                    "Closing socket"
                );
                ws.close();
            };
            this.ws = ws;

            // FIXME for debugging
            this.currentQueryId = foobar.queryId;
            this.handleMessage(foobar);
        },
        handleMessage: function (data) {
            console.log(data);
            if (data.status === "ERROR") {
                this.showError(data.message);
            } else if (data.status === "SUCCESS") {
                const queryId = data.queryId;
                if (this.currentQueryId === queryId) {
                    this.searchInProgress = false;
                    this.results = data.results;
                    this.currentQueryId = null;
                }
            }
        },
        submitQuery: function () {
            this.results = [];
            this.noSearchYet = false;
            this.searchInProgress = true;
            this.currentQueryId = uuidv4();
            this.ws.send(
                JSON.stringify({
                    action: "query_studies",
                    queryId: this.currentQueryId,
                    query: this.formData,
                })
            );
        },
        watchSelectAll: function (event) {
            const selectAll = event.target.checked;
            if (selectAll) {
                for (result of this.results) {
                    result.selected = true;
                }
            } else {
                for (result of this.results) {
                    delete result.selected;
                }
            }
            this.selectionChanged();
        },
        selectionChanged: function () {
            let allSelected = true;
            for (result of this.results) {
                if (!result.selected) {
                    allSelected = false;
                    break;
                }
            }
            this.selectAllChecked = allSelected;
        },
        submitTransfer: function () {
            const studiesToTransfer = this.results
                .filter(function (study) {
                    return !!study.selected;
                })
                .map(function (study) {
                    return {
                        PatientID: study.PatientID,
                        StudyInstanceUID: study.StudyInstanceUID,
                    };
                });

            console.log(JSON.stringify(studiesToTransfer));

            if (!this.formData.source) {
                this.showError("You must select a source.");
            } else if (!this.formData.destination) {
                this.showError("You must select a destination.");
            } else if (studiesToTransfer.length === 0) {
                this.showError("You must at least select one study.");
            } else {
                this.form.submit();
                console.log(this.form)
                // const csrftoken = document.querySelector(
                //     "[name=csrfmiddlewaretoken]"
                // ).value;

                // $.ajax({
                //     method: "POST",
                //     headers: { "X-CSRFToken": csrftoken },
                //     data: JSON.stringify(studiesToTransfer),
                // }).done(function(data, textStatus, jqXHR) {

                // }).fail(function(jqXHR, textStatus, errorThrown) {

                // });


            }
        },
        showError: function (text) {
            this.dispatch("main:add-message", {
                type: "alert-danger",
                text: text,
            });
        },
    };
}

// TODO Remove!
const foobar = {
    queryId: "dc9e071b-d8db-4b57-824b-76bad3f8c96c",
    status: "SUCCESS",
    results: [
        {
            SpecificCharacterSet: "ISO_IR 100",
            StudyDate: "20190915",
            StudyTime: "183223.0",
            AccessionNumber: "0062094332",
            QueryRetrieveLevel: "STUDY",
            StudyDescription: "MRT-Kopf",
            PatientName: "Banana^Ben",
            PatientID: "10002",
            PatientBirthDate: "19620218",
            StudyInstanceUID:
                "1.2.840.113845.11.1000000001951524609.20200705182751.2689480",
            Modalities: ["MR"],
        },
        {
            SpecificCharacterSet: "ISO_IR 100",
            StudyDate: "20180327",
            StudyTime: "180756.0",
            AccessionNumber: "0062115923",
            QueryRetrieveLevel: "STUDY",
            StudyDescription: "CT des Schädels",
            PatientName: "Banana^Ben",
            PatientID: "10002",
            PatientBirthDate: "19620218",
            StudyInstanceUID:
                "1.2.840.113845.11.1000000001951524609.20200705180932.2689477",
            Modalities: ["CT"],
        },
        {
            SpecificCharacterSet: "ISO_IR 100",
            StudyDate: "20180913",
            StudyTime: "185458.0",
            AccessionNumber: "0062115944",
            QueryRetrieveLevel: "STUDY",
            StudyDescription: "CT des Schädels",
            PatientName: "Banana^Ben",
            PatientID: "10002",
            PatientBirthDate: "19620218",
            StudyInstanceUID:
                "1.2.840.113845.11.1000000001951524609.20200705185333.2689485",
            Modalities: ["CT"],
        },
    ],
};
