const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");
const testConstants = require("../../testConstants.js");

const host = testConstants.host;
const projectsEndpoint = testConstants.projectsEndpoint;
const validID = 1;
const invalidID = 20;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/projects/:id endpoint API Calls - JSON", function () {
  beforeEach(async function () {
    child_process.spawn("java", ["-jar", "runTodoManagerRestAPI-1.5.5.jar"]);

    let serverReady = false;
    while (!serverReady) {
      try {
        await chai.request(host).get(projectsEndpoint);
        serverReady = true;
      } catch (err) {}
    }
  });

  afterEach(async function () {
    try {
      await chai.request(host).get("/shutdown");
    } catch (err) {}
  });

  it("GET /projects/:id - Returns project instance with specified existing id - Capability", async function () {
    const response = await chai
      .request(host)
      .get(`${projectsEndpoint}/${validID}`);
    const expected = {
      projects: [
        {
          id: "1",
          title: "Office Work",
          completed: "false",
          active: "false",
          description: "",
          tasks: [
            {
              id: "1",
            },
            {
              id: "2",
            },
          ],
        },
      ],
    };
    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("GET /projects/:id - Returns project instance with specified non-exisiting id - Error Case", async function () {
    const response = await chai
      .request(host)
      .get(`${projectsEndpoint}/${invalidID}`);
    const expected = {
      errorMessages: [`Could not find an instance with projects/${invalidID}`],
    };
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });

  it("HEAD /projects/:id - Return header for project with specified existing id - Capability", async function () {
    const response = await chai
      .request(host)
      .head(`${projectsEndpoint}/${validID}`);
    expect(response).to.have.status(200);
  });

  it("HEAD /projects/:id - Return header for project with specified non-existing id - Error Case", async function () {
    const response = await chai
      .request(host)
      .head(`${projectsEndpoint}/${invalidID}`);
    expect(response).to.have.status(404);
  });

  it("POST /projects/:id - Updates an existing project with fields passed through body - Capability", async function () {
    const response = await chai
      .request(host)
      .post(`${projectsEndpoint}/${validID}`)
      .send({
        active: true,
        description: "Meeting in progress",
      });

    const expected = {
      id: "1",
      title: "Office Work",
      completed: "false",
      active: "true",
      description: "Meeting in progress",
      tasks: [
        {
          id: "1",
        },
        {
          id: "2",
        },
      ],
    };
    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /projects/:id - Trying to update a non-existing project with fields passed through body - Error Case", async function () {
    const response = await chai
      .request(host)
      .post(`${projectsEndpoint}/${invalidID}`)
      .send({
        active: true,
        description: "Meeting in progress",
      });

    const expected = {
      errorMessages: [
        `No such project entity instance with GUID or ID ${invalidID} found`,
      ],
    };
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("PUT /projects/:id - Updates an existing project using put request with fields passed through body - Capability", async function () {
    const todoID = 1;
    const response = await chai
      .request(host)
      .put(`${projectsEndpoint}/${validID}`)
      .send({
        title: "University Work",
        active: true,
        description: "Meeting in progress",
      });
    const expected = {
      id: "1",
      title: "University Work",
      active: "true",
      completed: "false",
      description: "Meeting in progress",
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("PUT /projects/:id - Updates a non-existing project using put request with fields passed through body - Error Case", async function () {
    const todoID = 1;
    const response = await chai
      .request(host)
      .put(`${projectsEndpoint}/${invalidID}`)
      .send({
        title: "University Work",
        active: true,
        description: "Meeting in progress",
      });
    const expected = {
      errorMessages: [`Invalid GUID for ${invalidID} entity project`],
    };

    expect(response).to.have.status(404);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("DELETE /projects/:id - Deletes project using existing ID - Capability", async function () {
    const response = await chai
      .request(host)
      .delete(`${projectsEndpoint}/${validID}`);
    expect(response).to.have.status(200);
  });

  it("DELETE /projects/:id - Deletes project using non-existing ID - Error Case", async function () {
    const response = await chai
      .request(host)
      .delete(`${projectsEndpoint}/${invalidID}`);

    const expected = {
      errorMessages: [
        `Could not find any instances with projects/${invalidID}`,
      ],
    };

    expect(response).to.have.status(404);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });
});
