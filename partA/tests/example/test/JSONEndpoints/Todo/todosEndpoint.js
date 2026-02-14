const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../testConstants.js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const todosEndpoint = testConstants.todosEndpoint;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/todos endpoint API Calls - JSON", function () {
  beforeEach(async function () {
    child_process.spawn("java", ["-jar", "runTodoManagerRestAPI-1.5.5.jar"]);

    let serverReady = false;
    while (!serverReady) {
      try {
        await chai.request(host).get(todosEndpoint);
        serverReady = true;
      } catch (err) {}
    }
  });

  afterEach(async function () {
    try {
      await chai.request(host).get("/shutdown");
    } catch (err) {}
  });

  it("GET /todos - Returns all todos in memory - Capability", async function () {
    const response = await chai.request(host).get(todosEndpoint);
    const expected = {
      todos: [
        {
          id: "2",
          title: "file paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
        },
        {
          id: "1",
          title: "scan paperwork",
          doneStatus: "false",
          description: "",
          categories: [
            {
              id: "1",
            },
          ],
          tasksof: [
            {
              id: "1",
            },
          ],
        },
      ],
    };
    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("GET /todos?:doneStatus=bool - Returns all todos with doneStatus equal to bool - Capability", async function () {
    const response = await chai
      .request(host)
      .get(todosEndpoint)
      .query({ doneStatus: "false" });
    const expected = {
      todos: [
        {
          id: "1",
          title: "scan paperwork",
          doneStatus: "false",
          description: "",
          categories: [
            {
              id: "1",
            },
          ],
          tasksof: [
            {
              id: "1",
            },
          ],
        },
        {
          id: "2",
          title: "file paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
        },
      ],
    };
    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("GET /todos?:doneStatus=bool&description='' - Returns all todos with doneStatus equal to bool and description equal to string - Capability", async function () {
    const response = await chai
      .request(host)
      .get(todosEndpoint)
      .query({ doneStatus: "false", title: "file paperwork" });
    const expected = {
      todos: [
        {
          id: "2",
          title: "file paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
        },
      ],
    };
    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /todos - Create a todo w/out ID - Capability", async function () {
    const body = {
      title: "feed dog",
      doneStatus: false,
      description: "give him food",
    };
    const response = await chai.request(host).post(todosEndpoint).send(body);
    const expected = {
      id: "3",
      title: "feed dog",
      doneStatus: "false",
      description: "give him food",
    };

    expect(response).to.have.status(201);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /todos - Create a todo w/out ID with missing title - Error Case: MALFORMED JSON", async function () {
    const body = {
      doneStatus: false,
      description: "give him food",
    };
    const expected = {
      errorMessages: ["title : field is mandatory"],
    };
    const response = await chai.request(host).post(todosEndpoint).send(body);
    expect(response).to.have.status(400);
    expect(response.body).to.deep.equal(expected);
  });

  it("POST /todos - Create a todo w/ an extra random attribute - Error Case: MALFORMED JSON", async function () {
    const body = {
      title: "Feed my dog",
      doneStatus: false,
      description: "give him food",
      monthCreated: "OCT",
    };
    const expected = {
      errorMessages: ["Could not find field: monthCreated"],
    };
    const response = await chai.request(host).post(todosEndpoint).send(body);
    expect(response).to.have.status(400);
    expect(response.body).to.deep.equal(expected);
  });

  it("HEAD /todos - Return header for todos - Capability", async function () {
    const response = await chai.request(host).head(todosEndpoint);
    expect(response).to.have.status(200);
  });
});
