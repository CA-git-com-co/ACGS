// Constitutional Hash: cdd01ef066bc6cf2
package apiform

type Marshaler interface {
	MarshalMultipart() ([]byte, string, error)
}
