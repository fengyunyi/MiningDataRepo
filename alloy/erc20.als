// ERC20: https://github.com/OpenZeppelin/zeppelin-solidity/blob/master/contracts/token/ERC20/StandardToken.sol

// In solidity allowance is defined as mapping type:
// mapping (address => mapping (address => uint256)) allowance

// Note that "Mappings can be seen as hash tables which are virtually initialized 
// such that every possible key exists and is mapped to a value whose byte-representation is 
// all zeros: a type’s default value. The similarity ends here, though: The key data is not 
// actually stored in a mapping, only its keccak256 hash used to look up the value."

open util/ordering[TOKENBASE] as ord
sig Address{}


sig TOKENBASE{
	totalSupply: one Int, // in the smallest, nondividable unit
	balance: Address -> one Int,
	allowance: Address -> (Address -> Int),
	}

fact {all e: TOKENBASE| e.totalSupply > 0 }
//fact {all e: TOKENBASE| all a, b: Address| (e.allowance[a])[b] => 0}
//fact {all e: TOKENBASE, a: Address| e.balance[a] => 0}


// msg.sender(fromAddr) sends $value to another address (to_address)
pred transfer(toAddr, fromAddr: Address,  t, t': TOKENBASE, value: Int){
	value =< t.balance[fromAddr]
	value > 0
	fromAddr != toAddr
	
	t'.totalSupply = t.totalSupply
	t'.allowance = t.allowance
	
	let fromBal = t.balance[fromAddr] | 
		t'.balance = t.balance ++ (fromAddr -> minus[fromBal, value])
	let toBal = t.balance[toAddr] |
		t'.balance = t.balance ++ (toAddr -> plus[toBal, value])

}

// allow spender (expecting a contract but could be EOA) to withdraw from user's account, multiple times, up to the _value amount
// the spendable amount is min(balance, allowance) of a user account
// msg.sender is user
pred approve(spender, user: Address, t, t': TOKENBASE, value: Int){
	//preconditions
	value > 0
	spender != user

	// copy unchanged relations
	t'.totalSupply = t.totalSupply
	t'.balance = t.balance

	// not sure (user may not be in allowance)
	t'.allowance = t.allowance ++ (user -> (spender -> value))
}

// This is meant to be used with approve
// spender (msg.sender): expecting a contract (but can be called by EOA?)
// spender transfers $value fromAddr to toAddr as long as allowance[fromAddr][spender]>= value
// This function and aprove enable the scenario where a contract executes upon the payment of someone
pred transferFrom(spender, toAddr, fromAddr: Address, t, t': TOKENBASE, value: Int){
	//preconditions
	value > 0
	value =< t.balance[fromAddr]
	value =< t.allowance[fromAddr][spender]
	toAddr != fromAddr

	// copy unchanged relations
	t'.totalSupply = t.totalSupply

	let fromBal = t.balance[fromAddr] |
		t'.balance = t.balance ++ (fromAddr -> minus[fromBal, value])
	let toBal = t.balance[toAddr] |
		t'.balance = t.balance ++ (toAddr -> plus[toBal, value])
	let fromAllowed = t.allowance[fromAddr][spender] |
		t'.allowance = t.allowance ++ (fromAddr -> (spender -> minus[fromAllowed, value]))
}


// newly created ERC20 token by msg.sender
pred freshTOKENBASE(sender: Address, supply: Int, token: TOKENBASE) {
	supply > 0
	token.totalSupply = supply
	all a: Address - sender | token.balance[a] = 0
	all a, b: Address - sender | token.allowance[a][b] = 0
	token.balance[sender] = supply
	token.allowance[sender][sender] = supply
}

// states of the token
fact traces {
	// the first state is a freshly created token
	some creator: Address, sup: Int | sup > 0 && freshTOKENBASE[creator, sup, ord/first]

	all ts: TOKENBASE - ord/last | // for all token states except the last
		let ts' = ts.next |
			(some a1, a2: Address, val: Int | transfer[a1, a2, ts, ts', val])
			or (some a1, a2: Address, val: Int | approve[a1, a2, ts, ts', val])
			or (some a1, a2, a3: Address, val: Int | transferFrom[a1, a2, a3, ts, ts', val])
}

// total balance == totalSupply should always hold
//assert totalBalance {
//	all token: ERC20 | token.totalSupply = (sum b: Address | token.balance[b])
//}
assert positive{all e: TOKENBASE| all a, b: Address| e.allowance[a][b] >= 0}
//check totalBalance for 6 but 4 Address
run {} for 8 but 4 Address
