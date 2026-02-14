const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../testConstants.js");
const chaiXml = require("chai-xml");
const convert = require("xml-js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const todosEndpoint = testConstants.todosEndpoint;

chai.use(chaiHttp);
chai.use(chaiXml);
chai.use(deepEqualInAnyOrder);

describe("/todos endpoint API Calls - XML", function () {
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

  it("POST /todos - Create a todo w/out ID - Capability", async function () {
    const body = `<todo>
        <title>Clean Cupboard</title>
        <doneStatus>false</doneStatus>
        <description>Home Chore to be done</description>
      </todo>`;
    const response = await chai
      .request(host)
      .post(todosEndpoint)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected = {
      id: "3",
      title: "Clean Cupboard",
      doneStatus: "false",
      description: "Home Chore to be done",
    };
    expect(response).to.have.status(201);
    expect(response.body).to.deep.equal(expected);
  });

  it("POST /todos - Create a todo w/out ID with missing title - Error Case: MALFORMED XML", async function () {
    const body = `<todo>
        <doneStatus>false</doneStatus>
        <description>Give him food</description>
      </todo>`;
    const expected = {
      errorMessages: ["title : field is mandatory"],
    };
    const response = await chai
      .request(host)
      .post(todosEndpoint)
      .set("Content-Type", "application/xml")
      .send(body);
    expect(response).to.have.status(400);
    expect(response.body).to.deep.equal(expected);
  });

  it("POST /todos - Create a todo w/ an extra random attribute - Error Case: MALFORMED XML", async function () {
    const body = `<todo>
  <title>Clean Cupboard</title>
  <doneStatus>false</doneStatus>
  <description>Home Chore to be done</description>
  <monthCreated>OCT</monthCreated>
</todo>`;
    const expected = {
      errorMessages: ["Could not find field: monthCreated"],
    };
    const response = await chai
      .request(host)
      .post(todosEndpoint)
      .set("Content-Type", "application/xml")
      .send(body);
    expect(response).to.have.status(400);
    expect(response.body).to.deep.equal(expected);
  });

  it("HEAD /todos - Return header for todos - Capability", async function () {
    const response = await chai
      .request(host)
      .head(todosEndpoint)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);
  });
});
