const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../testConstants.js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const categoriesEndpoint = testConstants.categsEndpoint;
const validID = 1;
const invalidID = 20;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/categories/:id endpoint API Calls - XML", function () {
  beforeEach(async function () {
    child_process.spawn("java", ["-jar", "runTodoManagerRestAPI-1.5.5.jar"]);

    let serverReady = false;
    while (!serverReady) {
      try {
        await chai.request(host).get(categoriesEndpoint);
        serverReady = true;
      } catch (err) {}
    }
  });

  afterEach(async function () {
    try {
      await chai.request(host).get("/shutdown");
    } catch (err) {}
  });

  it("HEAD /categories/:id - Return header for category with specified existing id - Capability", async function () {
    const response = await chai
      .request(host)
      .head(`${categoriesEndpoint}/${validID}`)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);
  });

  it("HEAD /categories/:id - Return header for category with specified nonexistent id - Error Case", async function () {
    const response = await chai
      .request(host)
      .head(`${categoriesEndpoint}/${invalidID}`)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(404);
  });

  it("POST /categories/:id - amend an instance of a category with specific existing id - Capability", async function () {
    const body = `<category>
        <title>College</title>
    </category>`;
    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${validID}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected = {
      id: "1",
      title: "College",
      description: "",
    };
    expect(response).to.have.status(200);
    expect(response.body).to.deep.equal(expected);
  });

  it("POST /categories/:id - amend an instance of a category with specific nonexistent id - Error Case", async function () {
    const body = `<category>
            <title>College</title>
        </category>`;
    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${invalidID}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected = {
      errorMessages: [
        `No such category entity instance with GUID or ID ${invalidID} found`,
      ],
    };
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("PUT /categories/:id - amend an instance of a category with specific existing id - Capability", async function () {
    const body = `<category>
            <title>College</title>
        </category>`;
    const response = await chai
      .request(host)
      .put(`${categoriesEndpoint}/${validID}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected = { id: "1", title: "College", description: "" };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equal(expected);
  });

  it("PUT /categories/:id - amend an instance of a category with specific nonexistent id - Error Case", async function () {
    const body = `<category>
            <title>College</title>
        </category>`;
    const response = await chai
      .request(host)
      .put(`${categoriesEndpoint}/${invalidID}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected = {
      errorMessages: [`Invalid GUID for ${invalidID} entity category`],
    };

    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });

  it("DELETE /categories/:id - delete a specific instance of a category with specific existing id - Capability", async function () {
    const response = await chai
      .request(host)
      .delete(`${categoriesEndpoint}/${validID}`)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);
  });

  it("DELETE /categories/:id - delete a specific instance of a category with specific nonexistent id - Error Case", async function () {
    const expected = {
      errorMessages: [
        `Could not find any instances with categories/${invalidID}`,
      ],
    };
    const response = await chai
      .request(host)
      .delete(`${categoriesEndpoint}/${invalidID}`)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });
});
