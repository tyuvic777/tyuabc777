package main

import (
    "encoding/json"
    "fmt"
    "crypto/sha256"
    "encoding/hex"
    "time"
    "strconv"
    "errors"
    "github.com/hyperledger/fabric-chaincode-go/shim"
    pb "github.com/hyperledger/fabric-protos-go/peer"
)

// Structs
type PatientRecord struct {
    ID             string    `json:"id"`
    DataHash       string    `json:"data_hash"`
    CreatedAt      time.Time `json:"created_at"`
    UpdatedAt      time.Time `json:"updated_at"`
    Nonce          string    `json:"nonce"`
}

type PatientCareChaincode struct {}

// Init function
func (t *PatientCareChaincode) Init(stub shim.ChaincodeStubInterface) pb.Response {
    return shim.Success(nil)
}

// Invoke function with input validation and nonce-based replay protection
func (t *PatientCareChaincode) Invoke(stub shim.ChaincodeStubInterface) pb.Response {
    function, args := stub.GetFunctionAndParameters()

    switch function {
    case "createRecord":
        return t.createRecord(stub, args)
    case "updateRecord":
        return t.updateRecord(stub, args)
    case "getRecord":
        return t.getRecord(stub, args)
    default:
        return shim.Error("Invalid function name. Supported: createRecord, updateRecord, getRecord")
    }
}

// Helper function for secure hash generation
func generateHash(data string) string {
    hash := sha256.Sum256([]byte(data))
    return hex.EncodeToString(hash[:])
}

// Validate input length and format
func validateInput(input string, maxLength int) error {
    if len(input) == 0 || len(input) > maxLength {
        return errors.New("Invalid input length")
    }
    return nil
}

// Validate nonce for replay attack prevention
func validateNonce(stub shim.ChaincodeStubInterface, nonce string) error {
    existing, err := stub.GetState(nonce)
    if err != nil {
        return errors.New("Error checking nonce")
    }
    if existing != nil {
        return errors.New("Replay attack detected: Nonce already used")
    }
    return stub.PutState(nonce, []byte("used"))
}

// Create a new patient record securely
func (t *PatientCareChaincode) createRecord(stub shim.ChaincodeStubInterface, args []string) pb.Response {
    if len(args) != 2 {
        return shim.Error("Expected arguments: record ID, data hash")
    }

    id, dataHash := args[0], args[1]
    nonce := fmt.Sprintf("nonce-%s-%d", id, time.Now().UnixNano())

    if err := validateInput(id, 50); err != nil {
        return shim.Error(err.Error())
    }
    if err := validateInput(dataHash, 64); err != nil {
        return shim.Error(err.Error())
    }
    if err := validateNonce(stub, nonce); err != nil {
        return shim.Error(err.Error())
    }

    record := PatientRecord{
        ID:        id,
        DataHash:  dataHash,
        CreatedAt: time.Now(),
        UpdatedAt: time.Now(),
        Nonce:     nonce,
    }

    recordJSON, err := json.Marshal(record)
    if err != nil {
        return shim.Error("Failed to marshal record JSON")
    }
    stub.PutState(id, recordJSON)

    return shim.Success([]byte("Record created successfully"))
}

// Retrieve a patient record
func (t *PatientCareChaincode) getRecord(stub shim.ChaincodeStubInterface, args []string) pb.Response {
    if len(args) != 1 {
        return shim.Error("Expected argument: record ID")
    }
    id := args[0]
    if err := validateInput(id, 50); err != nil {
        return shim.Error(err.Error())
    }

    recordBytes, err := stub.GetState(id)
    if err != nil || recordBytes == nil {
        return shim.Error("Record not found")
    }

    return shim.Success(recordBytes)
}

// Update an existing patient record
func (t *PatientCareChaincode) updateRecord(stub shim.ChaincodeStubInterface, args []string) pb.Response {
    if len(args) != 2 {
        return shim.Error("Expected arguments: record ID, new data hash")
    }
    id, newDataHash := args[0], args[1]
    nonce := fmt.Sprintf("nonce-%s-%d", id, time.Now().UnixNano())

    if err := validateInput(id, 50); err != nil {
        return shim.Error(err.Error())
    }
    if err := validateInput(newDataHash, 64); err != nil {
        return shim.Error(err.Error())
    }
    if err := validateNonce(stub, nonce); err != nil {
        return shim.Error(err.Error())
    }

    existingBytes, err := stub.GetState(id)
    if err != nil || existingBytes == nil {
        return shim.Error("Record does not exist")
    }

    var record PatientRecord
    json.Unmarshal(existingBytes, &record)
    record.DataHash = newDataHash
    record.UpdatedAt = time.Now()
    record.Nonce = nonce

    recordJSON, err := json.Marshal(record)
    if err != nil {
        return shim.Error("Failed to marshal updated record JSON")
    }
    stub.PutState(id, recordJSON)

    return shim.Success([]byte("Record updated successfully"))
}

// Main function
func main() {
    err := shim.Start(new(PatientCareChaincode))
    if err != nil {
        fmt.Printf("Error starting PatientCareChaincode: %s", err)
    }
}
