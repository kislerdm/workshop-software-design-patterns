package main

import (
	"errors"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
)

func NewPubSub() *PubSub {
	return &PubSub{
		records: recordsContainer{
			mu:   &sync.RWMutex{},
			data: map[string][][]byte{},
		},
		consumers: consumersContainer{
			mu:   &sync.RWMutex{},
			data: map[string]map[string]uint{},
		},
	}
}

type recordsContainer struct {
	mu   *sync.RWMutex
	data map[string][][]byte
}

type consumersContainer struct {
	mu   *sync.RWMutex
	data map[string]map[string]uint
}

type PubSub struct {
	// map[topic][]record
	records recordsContainer

	// map[topic]map[consumerID]offset
	consumers consumersContainer
}

func (p *PubSub) Write(topic string, data []byte) (int, error) {
	p.records.mu.Lock()
	if _, ok := p.records.data[topic]; !ok {
		p.records.data[topic] = [][]byte{}
	}
	p.records.data[topic] = append(p.records.data[topic], data)
	l := len(p.records.data[topic])
	p.records.mu.Unlock()
	return l, nil
}

func (p *PubSub) Read(topic, clientID string, fromStart bool) (data []byte, err error) {
	p.records.mu.RLock()
	records, ok := p.records.data[topic]
	if !ok {
		err = errors.New("topic " + topic + " does not exist")
		p.records.mu.RUnlock()
		return
	}
	p.records.mu.RUnlock()

	last := uint(len(records))

	p.consumers.mu.Lock()
	var offset uint
	if _, ok = p.consumers.data[topic]; !ok {
		p.consumers.data[topic] = map[string]uint{
			clientID: last,
		}
	}
	if _, ok = p.consumers.data[topic][clientID]; !ok {
		p.consumers.data[topic][clientID] = last
	}
	p.consumers.mu.Unlock()

	p.consumers.mu.RLock()
	offset = p.consumers.data[topic][clientID]
	if fromStart {
		offset = 0
	}
	p.consumers.mu.RUnlock()

	if len(records) == int(offset) {
		return
	}

	p.records.mu.RLock()
	data = records[offset]
	p.records.mu.RUnlock()

	p.consumers.mu.Lock()
	p.consumers.data[topic][clientID] = offset + 1
	p.consumers.mu.Unlock()
	return
}

type handler struct {
	p *PubSub
}

func (h handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	const (
		publishPrefix = "publish"
		consumePrefix = "consume"
	)

	w.Header().Set("Content-Type", "application/json")

	pathElements := strings.Split(r.URL.Path, "/")[1:]
	switch pathElements[0] {
	case publishPrefix:
		if len(pathElements) != 2 {
			w.WriteHeader(http.StatusBadRequest)
			_, _ = w.Write([]byte(`{"error":"wrong endpoint"}`))
			return
		}

		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			_, _ = w.Write([]byte(`{"error":"wrong method"}`))
			return
		}

		defer func() { _ = r.Body.Close() }()

		data, err := io.ReadAll(r.Body)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			_, _ = w.Write([]byte(`{"error":"corrupt record"}`))
			return
		}

		offset, err := h.p.Write(pathElements[1], data)

		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			_, _ = w.Write([]byte(`{"error":"internal error"}`))
			return
		}

		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"offset":` + strconv.Itoa(offset) + `}`))

		return

	case consumePrefix:
		if len(pathElements) != 3 {
			w.WriteHeader(http.StatusBadRequest)
			_, _ = w.Write([]byte(`{"error":"wrong endpoint"}`))
			return
		}

		if r.Method != http.MethodGet {
			w.WriteHeader(http.StatusMethodNotAllowed)
			_, _ = w.Write([]byte(`{"error":"wrong method"}`))
			return
		}

		var fromStart bool

		query := r.URL.Query()
		if len(query) > 0 {
			fromStart, _ = strconv.ParseBool(query["from_start"][0])
		}

		data, err := h.p.Read(pathElements[1], pathElements[2], fromStart)
		if err != nil {
			w.WriteHeader(http.StatusNotFound)
			_, _ = w.Write([]byte(`{"error":"` + err.Error() + `"}`))
			return
		}

		if len(data) == 0 {
			w.WriteHeader(http.StatusNoContent)
		} else {
			w.WriteHeader(http.StatusOK)
		}
		_, _ = w.Write(data)
		return

	default:
		w.WriteHeader(http.StatusNotFound)
		_, _ = w.Write([]byte(`{"error":"wrong endpoint"}`))
		return
	}
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "9000"
	}

	if err := http.ListenAndServe(":"+port, handler{p: NewPubSub()}); err != nil {
		log.Fatalln(err)
	}
}
