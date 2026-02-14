const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");
const { host } = require("../../testConstants.js");

const projectsEndpoint = "/projects";

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/projects endpoint API Calls - XML", function () {
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

  it("HEAD /projects - Return header for projects - Capability", async function () {
    const response = await chai
      .request(host)
      .head(projectsEndpoint)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);
  });

  it("POST /projects - Create a todo w/out ID - Capability", async function () {
    const body = `<project>
        <active>false</active>
        <description>Meeting for 429 group</description>
        <completed>false</completed>
        <title>School</title>    
    </project>`;

    const response = await chai
      .request(host)
      .post(projectsEndpoint)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected = {
      id: "2",
      title: "School",
      completed: "false",
      description: "Meeting for 429 group",
      active: "false",
    };
    expect(response).to.have.status(201);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /projects - Create a project w/out ID with inavlid input type for active status - Error Case", async function () {
    const body = `<project>
        <active>yes</active>
        <description>Write unit tests for 429</description>
        <completed>false</completed>
        <title>429 autoproj</title>    
    </project>`;

    const response = await chai
      .request(host)
      .post(projectsEndpoint)
      .set("Content-Type", "application/xml")
      .send(body);
    expect(response).to.have.status(400);
    expect(response.body).to.deep.equal({
      errorMessages: ["Failed Validation: active should be BOOLEAN"],
    });
  });
});
